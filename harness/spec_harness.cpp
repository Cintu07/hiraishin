// hiraishin step 1 harness: plain greedy decode, chain speculative decode with per-cycle timing,
// verify-cost vs batch size, and a batch-invariance check. Built against llama.cpp (PrismML fork e8fd209).
//
// Every number this prints comes from llama_synchronize()-bounded wall clock timers.
// Output: one JSON object per line on stdout; token ids and text per run under --out.

#include "llama.h"
#include "ggml-backend.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

using clk = std::chrono::steady_clock;
static double ms_since(clk::time_point t0) {
    return std::chrono::duration<double, std::milli>(clk::now() - t0).count();
}

struct args_t {
    std::string target, draft, out = "harness_out";
    std::vector<std::string> prompts;
    std::vector<int> ks = {2, 4, 8};
    std::vector<float> taus = {0.0f};
    std::vector<int> inv_bs = {2, 3, 5, 9};
    int n_predict = 256, n_ctx = 2048, reps = 1;
    bool verify_cost = true, invariance = true, pad_guard = true, draft_probe = false, draft_b2 = true;
};

static std::vector<int> parse_list(const char * s) {
    std::vector<int> v;
    std::stringstream ss(s);
    std::string x;
    while (std::getline(ss, x, ',')) v.push_back(std::atoi(x.c_str()));
    return v;
}

static args_t parse(int argc, char ** argv) {
    args_t a;
    for (int i = 1; i < argc; i++) {
        std::string k = argv[i];
        auto next = [&]() { if (i + 1 >= argc) { fprintf(stderr, "missing value for %s\n", k.c_str()); exit(1); } return argv[++i]; };
        if      (k == "-m")      a.target = next();
        else if (k == "-md")     a.draft = next();
        else if (k == "-f")      a.prompts.push_back(next());
        else if (k == "-n")      a.n_predict = std::atoi(next());
        else if (k == "-c")      a.n_ctx = std::atoi(next());
        else if (k == "-k")      a.ks = parse_list(next());
        else if (k == "--inv-b") a.inv_bs = parse_list(next());
        else if (k == "--tau") {
            a.taus.clear();
            std::stringstream ss(next());
            std::string x;
            while (std::getline(ss, x, ',')) a.taus.push_back(std::strtof(x.c_str(), nullptr));
        }
        else if (k == "--reps")  a.reps = std::atoi(next());
        else if (k == "--out")   a.out = next();
        else if (k == "--no-verify-cost") a.verify_cost = false;
        else if (k == "--no-invariance")  a.invariance = false;
        else if (k == "--no-pad-guard")   a.pad_guard = false;
        else if (k == "--draft-probe")    a.draft_probe = true;
        else if (k == "--no-draft-b2")    a.draft_b2 = false;
        else { fprintf(stderr, "unknown arg %s\n", k.c_str()); exit(1); }
    }
    if (a.target.empty() || a.prompts.empty()) {
        fprintf(stderr, "usage: spec_harness -m target.gguf [-md draft.gguf] -f prompt.txt [-f ...] [-n 256] [-k 2,4,8] [--out dir]\n");
        exit(1);
    }
    return a;
}

// same as llama.cpp common -f: read file, drop exactly one trailing '\n'
static std::string read_prompt(const std::string & path) {
    std::ifstream f(path, std::ios::binary);
    std::string s((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    if (!s.empty() && s.back() == '\n') s.pop_back();
    return s;
}

static std::string basename_noext(const std::string & p) {
    size_t a = p.find_last_of("/\\");
    std::string b = a == std::string::npos ? p : p.substr(a + 1);
    size_t d = b.rfind('.');
    return d == std::string::npos ? b : b.substr(0, d);
}

struct model_t {
    llama_model * model = nullptr;
    llama_context * ctx = nullptr;
    const llama_vocab * vocab = nullptr;
    int n_vocab = 0;
    llama_batch batch{};
    llama_memory_t mem() const { return llama_get_memory(ctx); }
};

static model_t load(const std::string & path, int n_ctx) {
    model_t m;
    auto mp = llama_model_default_params();
    mp.n_gpu_layers = 999;
    m.model = llama_model_load_from_file(path.c_str(), mp);
    if (!m.model) { fprintf(stderr, "failed to load %s\n", path.c_str()); exit(1); }
    auto cp = llama_context_default_params();
    cp.n_ctx = n_ctx;
    cp.n_batch = n_ctx;
    cp.n_ubatch = 512;
    cp.n_seq_max = 1;
    cp.flash_attn_type = LLAMA_FLASH_ATTN_TYPE_ENABLED;
    cp.no_perf = true;
    m.ctx = llama_init_from_model(m.model, cp);
    if (!m.ctx) { fprintf(stderr, "failed to create context for %s\n", path.c_str()); exit(1); }
    m.vocab = llama_model_get_vocab(m.model);
    m.n_vocab = llama_vocab_n_tokens(m.vocab);
    m.batch = llama_batch_init(n_ctx, 0, 1);
    return m;
}

// decode toks at positions [pos0, pos0+n); logits for all positions if all_logits, else only the last.
// returns wall ms including llama_synchronize (so the GPU work is complete).
static double decode(model_t & m, const llama_token * toks, int n, int pos0, bool all_logits) {
    llama_batch & b = m.batch;
    b.n_tokens = n;
    for (int i = 0; i < n; i++) {
        b.token[i] = toks[i];
        b.pos[i] = pos0 + i;
        b.n_seq_id[i] = 1;
        b.seq_id[i][0] = 0;
        b.logits[i] = all_logits || i == n - 1;
    }
    auto t0 = clk::now();
    int rc = llama_decode(m.ctx, b);
    llama_synchronize(m.ctx);
    double t = ms_since(t0);
    if (rc != 0) { fprintf(stderr, "llama_decode rc=%d (n=%d pos0=%d)\n", rc, n, pos0); exit(1); }
    return t;
}

struct top2 { llama_token id; float l1, l2; };

// first index of the maximum, same tie rule as llama_sampler_greedy
static top2 argmax2(const float * l, int n) {
    int best = 0;
    float b1 = l[0], b2 = -INFINITY;
    for (int i = 1; i < n; i++) {
        if (l[i] > b1) { b2 = b1; b1 = l[i]; best = i; }
        else if (l[i] > b2) { b2 = l[i]; }
    }
    return {best, b1, b2};
}

static std::vector<llama_token> tokenize(const model_t & m, const std::string & s) {
    std::vector<llama_token> t(s.size() + 16);
    int n = llama_tokenize(m.vocab, s.c_str(), (int) s.size(), t.data(), (int) t.size(), true, true);
    if (n < 0) { t.resize(-n); n = llama_tokenize(m.vocab, s.c_str(), (int) s.size(), t.data(), (int) t.size(), true, true); }
    t.resize(n);
    return t;
}

static std::string detok(const model_t & m, const std::vector<llama_token> & ts) {
    std::string out;
    char buf[256];
    for (auto t : ts) {
        int n = llama_token_to_piece(m.vocab, t, buf, sizeof(buf), 0, false);
        if (n > 0) out.append(buf, n);
    }
    return out;
}

static void write_run(const args_t & a, const std::string & tag, const model_t & m, const std::vector<llama_token> & ts) {
    {
        std::ofstream f(a.out + "/" + tag + ".ids");
        for (auto t : ts) f << t << "\n";
    }
    std::ofstream f(a.out + "/" + tag + ".txt", std::ios::binary);
    f << detok(m, ts);
}

static double median(std::vector<double> v) {
    std::sort(v.begin(), v.end());
    return v.empty() ? 0 : v[v.size() / 2];
}

// process the prompt in one batch (as llama-completion does) and return argmax of the last position
static top2 prefill(model_t & m, const std::vector<llama_token> & p) {
    llama_memory_clear(m.mem(), true);
    decode(m, p.data(), (int) p.size(), 0, false);
    return argmax2(llama_get_logits_ith(m.ctx, -1), m.n_vocab);
}

struct plain_result { std::vector<llama_token> ids; std::vector<top2> tops; double ms_total; std::vector<double> step_ms; };

static plain_result run_plain(model_t & t, const std::vector<llama_token> & p, int n_predict) {
    plain_result r;
    top2 cur = prefill(t, p);
    int pos = (int) p.size();
    auto t0 = clk::now();
    r.ids.push_back(cur.id);
    r.tops.push_back(cur);
    while ((int) r.ids.size() < n_predict && !llama_vocab_is_eog(t.vocab, cur.id)) {
        auto ts = clk::now();
        decode(t, &cur.id, 1, pos++, false);
        cur = argmax2(llama_get_logits_ith(t.ctx, -1), t.n_vocab);
        r.step_ms.push_back(ms_since(ts));
        r.ids.push_back(cur.id);
        r.tops.push_back(cur);
    }
    r.ms_total = ms_since(t0);
    return r;
}

struct spec_result {
    std::vector<llama_token> ids;
    int cycles = 0, n_drafted = 0, n_accept = 0, n_generated = 0;  // n_generated: before truncation to n_predict
    int n_clipped = 0;  // cycles whose draft length was shortened by the KV_PAD guard
    double ms_draft_first = 0;    // part of ms_draft_gpu: the first draft decode of each cycle (catch-up batch)
    int n_draft_first_multi = 0;  // cycles whose catch-up batch had more than one token
    double ms_total = 0, ms_draft_gpu = 0, ms_draft_cpu = 0, ms_verify_gpu = 0, ms_verify_cpu = 0, ms_kv = 0;
    std::vector<int> accepted_per_cycle;
};

// llama.cpp sizes the attention KV range as n_kv = pad(highest position + 1, KV_PAD) (llama-kv-cache.cpp,
// get_n_kv). A token decoded alone at position p attends over pad(p + 1) cells; inside a batch it attends over
// pad(last batch position + 1). When a batch crosses a multiple of KV_PAD those differ, the flash-attention
// KV split changes, and the logits are no longer bit-identical. Keeping every verify window inside one
// KV_PAD block makes the attention shape the same as in plain decoding.
static const int KV_PAD = 256;

// largest B such that a batch at positions [pos, pos + B) stays inside the KV_PAD block of pos
static int pad_room(int pos) {
    const int lim = ((pos + 1 + KV_PAD - 1) / KV_PAD) * KV_PAD;
    return lim - pos;
}

// chain speculative decoding, greedy: lossless w.r.t. the batched target logits by construction, and w.r.t.
// plain decoding when those are bit-identical to batch-1 logits (see the invariance test).
// tau > 0: adaptive draft length, stop drafting after a token whose draft logit margin (top1 - top2) is below tau
static spec_result run_spec(model_t & t, model_t & d, const std::vector<llama_token> & p, int n_predict, int k,
                            bool pad_guard, float tau, bool draft_b2) {
    spec_result r;
    top2 first = prefill(t, p);
    llama_memory_clear(d.mem(), true);
    decode(d, p.data(), (int) p.size(), 0, false);  // draft prompt prefill, outside the timed loop like the target's

    // all = prompt + emitted tokens; the last one ("pending") is not yet in the target KV cache
    std::vector<llama_token> all(p);
    all.push_back(first.id);
    r.ids.push_back(first.id);
    int n_past_t = (int) p.size();  // target KV length == all.size() - 1
    int n_past_d = (int) p.size();  // draft KV length, its cells always hold all[0 .. n_past_d)

    std::vector<llama_token> vb(k + 1), dr(k);
    auto t0 = clk::now();
    while ((int) r.ids.size() < n_predict && !llama_vocab_is_eog(t.vocab, all.back())) {
        const llama_token pending = all.back();
        const int k_room = pad_guard ? std::min(k, pad_room(n_past_t) - 1) : k;
        if (k_room < k) r.n_clipped++;

        // ---- draft up to k_room tokens (the draft first catches up on every committed token it has not seen)
        int kk = 0;
        if (k_room > 0) {
            // token at a draft-side position: committed tokens, then this cycle's drafts
            auto tok_at = [&](int pos) { return pos < (int) all.size() ? all[pos] : dr[pos - (int) all.size()]; };
            // fixed shape: every draft decode is exactly 2 tokens (re-decoding the previous token), because
            // switching between 1- and 2-token batches rebuilds the graph each time (see draft_probe)
            auto draft_decode_to = [&](int end) {  // make the draft KV hold positions [0, end)
                double ms = 0;
                if (draft_b2) {
                    if (end - n_past_d == 1 && n_past_d > 0) {
                        llama_memory_seq_rm(d.mem(), 0, n_past_d - 1, -1);
                        n_past_d--;
                    }
                    while (end - n_past_d > 2) {  // rare: long catch-up, feed in pairs
                        llama_token pr[2] = {tok_at(n_past_d), tok_at(n_past_d + 1)};
                        ms += decode(d, pr, 2, n_past_d, false);
                        n_past_d += 2;
                    }
                }
                std::vector<llama_token> buf;
                for (int q = n_past_d; q < end; q++) buf.push_back(tok_at(q));
                ms += decode(d, buf.data(), (int) buf.size(), n_past_d, false);
                n_past_d = end;
                return ms;
            };
            const int n_feed = (int) all.size() - n_past_d;
            const double ms_first = draft_decode_to((int) all.size());
            r.ms_draft_gpu += ms_first;
            r.ms_draft_first += ms_first;
            if (n_feed > 1) r.n_draft_first_multi++;
            for (int i = 0; i < k_room; i++) {
                if (i > 0) r.ms_draft_gpu += draft_decode_to((int) all.size() + i);
                auto tc = clk::now();
                const top2 g = argmax2(llama_get_logits_ith(d.ctx, -1), d.n_vocab);
                r.ms_draft_cpu += ms_since(tc);
                dr[kk++] = g.id;
                if (tau > 0 && g.l1 - g.l2 < tau) break;
            }
            // dr[kk-1] is never decoded on the draft here: its logits are not needed this cycle
        }
        r.n_drafted += kk;

        // ---- verify [pending, dr0..dr(kk-1)] in one target batch
        vb[0] = pending;
        for (int i = 0; i < kk; i++) vb[i + 1] = dr[i];
        r.ms_verify_gpu += decode(t, vb.data(), kk + 1, n_past_t, true);
        auto tc = clk::now();
        int m = 0;
        llama_token bonus = 0;
        for (int j = 0; j <= kk; j++) {
            llama_token g = argmax2(llama_get_logits_ith(t.ctx, j), t.n_vocab).id;
            if (j < kk && g == dr[j]) { m++; continue; }
            bonus = g;
            break;
        }
        r.ms_verify_cpu += ms_since(tc);

        // ---- bookkeeping: drop rejected positions from both KV caches
        auto tk = clk::now();
        const int committed = n_past_t + m + 1;  // pending + dr[0..m-1]
        llama_memory_seq_rm(t.mem(), 0, committed, -1);
        n_past_t = committed;
        if (n_past_d > committed) {
            llama_memory_seq_rm(d.mem(), 0, committed, -1);
            n_past_d = committed;
        }
        r.ms_kv += ms_since(tk);

        for (int i = 0; i < m; i++) { all.push_back(dr[i]); r.ids.push_back(dr[i]); }
        all.push_back(bonus);
        r.ids.push_back(bonus);
        r.n_accept += m;
        r.accepted_per_cycle.push_back(m);
        r.cycles++;
        // stop on eog inside the accepted run
        for (size_t i = r.ids.size() - (m + 1); i < r.ids.size(); i++) {
            if (llama_vocab_is_eog(t.vocab, r.ids[i])) {
                const size_t drop = r.ids.size() - (i + 1);
                r.ids.resize(i + 1);
                all.resize(all.size() - drop);
                break;
            }
        }
    }
    r.ms_total = ms_since(t0);
    r.n_generated = (int) r.ids.size();
    if ((int) r.ids.size() > n_predict) r.ids.resize(n_predict);
    return r;
}

int main(int argc, char ** argv) {
    args_t a = parse(argc, argv);
    ggml_backend_load_all();
    llama_backend_init();
    llama_log_set([](ggml_log_level lvl, const char * txt, void *) { if (lvl >= GGML_LOG_LEVEL_WARN) fputs(txt, stderr); }, nullptr);

    model_t t = load(a.target, a.n_ctx);
    model_t d;
    if (!a.draft.empty()) d = load(a.draft, a.n_ctx);
    printf("{\"event\":\"loaded\",\"target\":\"%s\",\"draft\":\"%s\",\"n_vocab\":%d}\n", a.target.c_str(), a.draft.c_str(), t.n_vocab);

    // warmup both models (kernel load, graph alloc)
    {
        auto p = tokenize(t, "warmup warmup warmup");
        for (int i = 0; i < 2; i++) { prefill(t, p); decode(t, &p[0], 1, (int) p.size(), false); }
        if (d.ctx) for (int i = 0; i < 2; i++) { prefill(d, p); decode(d, &p[0], 1, (int) p.size(), false); }
    }

    for (const auto & pf : a.prompts) {
        const std::string name = basename_noext(pf);
        auto prompt = tokenize(t, read_prompt(pf));

        plain_result ref;
        for (int rep = 1; rep <= a.reps; rep++) {
            plain_result pr = run_plain(t, prompt, a.n_predict);
            std::string tag = "plain_" + name + "_r" + std::to_string(rep);
            write_run(a, tag, t, pr.ids);
            int n_steps = (int) pr.step_ms.size();
            printf("{\"event\":\"plain\",\"prompt\":\"%s\",\"rep\":%d,\"n_prompt\":%zu,\"n\":%zu,\"ms_total\":%.3f,"
                   "\"tok_s\":%.3f,\"step_ms_median\":%.3f,\"same_as_rep1\":%s}\n",
                   name.c_str(), rep, prompt.size(), pr.ids.size(), pr.ms_total, n_steps / (pr.ms_total / 1e3),
                   median(pr.step_ms), rep == 1 ? "true" : (pr.ids == ref.ids ? "true" : "false"));
            if (rep == 1) ref = pr;
            fflush(stdout);
        }

        if (d.ctx) {
            for (int k : a.ks) {
              for (float tau : a.taus) {
                for (int rep = 1; rep <= a.reps; rep++) {
                    spec_result sr = run_spec(t, d, prompt, a.n_predict, k, a.pad_guard, tau, a.draft_b2);
                    char tau_s[32];
                    snprintf(tau_s, sizeof(tau_s), "%g", tau);
                    std::string tag = "spec_k" + std::to_string(k) + (tau > 0 ? std::string("_tau") + tau_s : "") + "_" + name + "_r" + std::to_string(rep);
                    write_run(a, tag, t, sr.ids);
                    int first_diff = -1;
                    for (size_t i = 0; i < std::min(sr.ids.size(), ref.ids.size()); i++) {
                        if (sr.ids[i] != ref.ids[i]) { first_diff = (int) i; break; }
                    }
                    if (first_diff < 0 && sr.ids.size() != ref.ids.size()) first_diff = (int) std::min(sr.ids.size(), ref.ids.size());
                    double margin = first_diff >= 0 && first_diff < (int) ref.tops.size() ? ref.tops[first_diff].l1 - ref.tops[first_diff].l2 : -1;
                    double other = sr.ms_total - sr.ms_draft_gpu - sr.ms_draft_cpu - sr.ms_verify_gpu - sr.ms_verify_cpu - sr.ms_kv;
                    printf("{\"event\":\"spec\",\"prompt\":\"%s\",\"k\":%d,\"tau\":%g,\"rep\":%d,\"n\":%zu,\"cycles\":%d,\"n_drafted\":%d,\"n_accept\":%d,"
                           "\"ms_total\":%.3f,\"tok_s\":%.3f,\"ms_draft_gpu\":%.3f,\"ms_draft_cpu\":%.3f,\"ms_verify_gpu\":%.3f,"
                           "\"ms_verify_cpu\":%.3f,\"ms_kv\":%.3f,\"ms_other\":%.3f,\"matches_plain\":%s,\"first_diff\":%d,"
                           "\"plain_margin_at_diff\":%.5f,\"pad_guard\":%s,\"n_clipped\":%d,\"ms_draft_first\":%.3f,\"n_draft_first_multi\":%d}\n",
                           name.c_str(), k, tau, rep, sr.ids.size(), sr.cycles, sr.n_drafted, sr.n_accept, sr.ms_total,
                           (sr.n_generated - 1) / (sr.ms_total / 1e3), sr.ms_draft_gpu, sr.ms_draft_cpu, sr.ms_verify_gpu,
                           sr.ms_verify_cpu, sr.ms_kv, other, first_diff < 0 ? "true" : "false", first_diff, margin,
                           a.pad_guard ? "true" : "false", sr.n_clipped, sr.ms_draft_first, sr.n_draft_first_multi);
                    fflush(stdout);
                }
              }
            }
        }

        // batch invariance: re-run the plain sequence through the target in windows of B tokens (teacher forcing,
        // exactly what verification with a perfect drafter would do) and compare argmax to plain batch-1 decode.
        if (a.invariance) {
            for (int B : a.inv_bs) {
                prefill(t, prompt);
                int pos = (int) prompt.size();
                int mism = 0, first = -1;
                double min_margin_mism = 1e9, max_dl1 = 0, first_nz_d = 0;
                int first_nz = -1, first_nz_pos = -1;  // first generated index / KV position whose top-1 logit differs at all
                // ref.ids[i] is the token produced after consuming ref.ids[0..i-1]; feed ids[0..] and predict ids[1..]
                for (size_t s = 0; s + 1 < ref.ids.size();) {
                    int n = (int) std::min<size_t>(B, ref.ids.size() - 1 - s);
                    if (a.pad_guard) n = std::min(n, pad_room(pos));
                    decode(t, &ref.ids[s], n, pos, true);
                    for (int j = 0; j < n; j++) {
                        top2 g = argmax2(llama_get_logits_ith(t.ctx, j), t.n_vocab);
                        const top2 & want = ref.tops[s + j + 1];
                        max_dl1 = std::max(max_dl1, (double) std::fabs(g.l1 - want.l1));
                        if (g.l1 != want.l1 && first_nz < 0) { first_nz = (int) (s + j + 1); first_nz_pos = pos + j; first_nz_d = g.l1 - want.l1; }
                        if (g.id != want.id) {
                            mism++;
                            if (first < 0) first = (int) (s + j + 1);
                            min_margin_mism = std::min(min_margin_mism, (double) (want.l1 - want.l2));
                        }
                    }
                    pos += n;
                    s += n;
                }
                printf("{\"event\":\"invariance\",\"prompt\":\"%s\",\"B\":%d,\"positions\":%zu,\"argmax_mismatches\":%d,"
                       "\"first_mismatch\":%d,\"max_abs_dlogit_top1\":%.6f,\"min_plain_margin_at_mismatch\":%.6f,\"pad_guard\":%s,"
                       "\"first_nonzero_idx\":%d,\"first_nonzero_kvpos\":%d,\"first_nonzero_dlogit\":%.6f,\"n_prompt\":%zu}\n",
                       name.c_str(), B, ref.ids.size() - 1, mism, first, max_dl1, mism ? min_margin_mism : -1.0,
                       a.pad_guard ? "true" : "false", first_nz, first_nz_pos, first_nz_d, prompt.size());
                fflush(stdout);
            }
        }

        // verify cost vs batch size at depth n_prompt + n_predict/2 (median of 15 after 3 warmups)
        if (a.verify_cost) {
            int depth = (int) prompt.size() + (int) ref.ids.size() / 2;
            std::vector<llama_token> ctx_toks(prompt);
            ctx_toks.insert(ctx_toks.end(), ref.ids.begin(), ref.ids.begin() + (ref.ids.size() / 2));
            for (model_t * m : {&t, &d}) {
                if (!m->ctx) continue;
                llama_memory_clear(m->mem(), true);
                decode(*m, ctx_toks.data(), depth, 0, false);
                int maxB = m == &t ? 12 : 1;
                for (int B = 1; B <= maxB; B++) {
                    std::vector<double> ts;
                    for (int it = 0; it < 18; it++) {
                        double ms = decode(*m, &ref.ids[0], B, depth, true);
                        llama_memory_seq_rm(m->mem(), 0, depth, -1);
                        if (it >= 3) ts.push_back(ms);
                    }
                    printf("{\"event\":\"verify_cost\",\"model\":\"%s\",\"prompt\":\"%s\",\"depth\":%d,\"B\":%d,\"ms_median\":%.4f,\"ms_min\":%.4f}\n",
                           m == &t ? "target" : "draft", name.c_str(), depth, B, median(ts), *std::min_element(ts.begin(), ts.end()));
                    fflush(stdout);
                }
            }
        }
    }

    // draft call-pattern probe: per-call cost of draft decodes in the patterns the speculative loop produces
    if (a.draft_probe && d.ctx) {
        auto p = tokenize(t, read_prompt(a.prompts[0]));
        const int n0 = (int) p.size();
        struct pat { const char * name; int mode; };
        // mode 0: B=1 back to back. 1: alternate B=2 / B=1. 2: B=1 with a target B=5 decode before each.
        // 3: B=2 back to back.
        for (pat pt : {pat{"draft_b1_only", 0}, pat{"draft_alt_b2_b1", 1}, pat{"draft_b1_after_target_b5", 2}, pat{"draft_b2_only", 3}}) {
            prefill(d, p);
            prefill(t, p);
            std::vector<double> ms_b1, ms_b2;
            int pos = n0;
            for (int it = 0; it < 40; it++) {
                if (pt.mode == 2) {
                    decode(t, p.data(), 5, n0, true);
                    llama_memory_seq_rm(t.mem(), 0, n0, -1);
                }
                const bool two = pt.mode == 3 || (pt.mode == 1 && it % 2 == 0);
                const double ms = decode(d, p.data(), two ? 2 : 1, pos, false);
                pos += two ? 2 : 1;
                if (pos > n0 + 200) { llama_memory_seq_rm(d.mem(), 0, n0, -1); pos = n0; }
                if (it >= 4) (two ? ms_b2 : ms_b1).push_back(ms);
            }
            printf("{\"event\":\"draft_probe\",\"pattern\":\"%s\",\"b1_ms_median\":%.4f,\"b2_ms_median\":%.4f,\"n_b1\":%zu,\"n_b2\":%zu}\n",
                   pt.name, median(ms_b1), median(ms_b2), ms_b1.size(), ms_b2.size());
            fflush(stdout);
        }
    }

    llama_batch_free(t.batch);
    llama_free(t.ctx);
    llama_model_free(t.model);
    if (d.ctx) { llama_batch_free(d.batch); llama_free(d.ctx); llama_model_free(d.model); }
    llama_backend_free();
    return 0;
}
