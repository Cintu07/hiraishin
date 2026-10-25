// hiraishin: making speculative verification bit-identical to plain decoding
// llama.cpp (PrismML fork e8fd209), RTX 5060 Laptop, Qwen3-8B

// 1) KV padding. llama.cpp attends over n_kv = pad(pos + 1, 256) cells.
//    A token decoded alone at 255 sees 256 cells; inside a batch ending at 257 it sees 512.
//    Fix: never let a verify window cross a 256 boundary.
static const int KV_PAD = 256;

static int pad_room(int pos) {
    const int lim = ((pos + 1 + KV_PAD - 1) / KV_PAD) * KV_PAD;
    return lim - pos;  // largest B with [pos, pos + B) inside one KV_PAD block
}

const int k_room = std::min(k, pad_room(n_past_t) - 1);  // draft length this cycle


// 2) Mat-vec. The K-loop stride and the cross-warp reduction both follow nwarps,
//    and nwarps depended on the column count. Every column now uses the one-column
//    value, so each column sums in exactly the order of a token decoded alone.
static constexpr int calc_nwarps(ggml_type type, int ncols_dst, mmvq_parameter_table_id table_id,
                                 bool small_k = false, bool halve_iters = false, bool bi = false) {
    if (bi && ncols_dst > 1 && ncols_dst <= MMVQ_MAX_BATCH_SIZE) {
        return calc_nwarps(type, 1, table_id, small_k, halve_iters, false);
    }
    // ... stock table
}


// 3) Flash attention. The KV split (parallel_blocks) is sized from the kernel's occupancy,
//    and the 1-query and 2-query kernels have different occupancy. Only shows up past KV 384.
fattn_kernel_t occupancy_kernel = nullptr;
if (cols_per_block > 1 && ggml_cuda_batch_invariant()) {
    occupancy_kernel = flash_attn_ext_vec<D, 1, type_K, type_V, use_logit_softcap>;
}
launch_fattn<D, cols_per_block, 1>(ctx, dst, fattn_kernel, nwarps, nbytes_shared, D,
                                   need_f16_K, need_f16_V, false, WARP_SIZE, occupancy_kernel);


// result: 208/208 speculative runs token-identical to plain decode,
//         max |logit diff| 0.000000 for batch sizes 2..16
