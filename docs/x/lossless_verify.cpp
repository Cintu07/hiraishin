// 1. kv pad: batch crossing 256 = diff attn len, so just dont cross it lol
static const int KV_PAD = 256;

static int pad_room(int pos) {
    const int lim = ((pos + 1 + KV_PAD - 1) / KV_PAD) * KV_PAD;
    return lim - pos;
}

const int k_room = std::min(k, pad_room(n_past_t) - 1);


// 2. matvec: every col uses the 1-col warp count, same sum order, no cap
static constexpr int calc_nwarps(ggml_type type, int ncols_dst, mmvq_parameter_table_id table_id,
                                 bool small_k = false, bool halve_iters = false, bool bi = false) {
    if (bi && ncols_dst > 1 && ncols_dst <= MMVQ_MAX_BATCH_SIZE) {
        return calc_nwarps(type, 1, table_id, small_k, halve_iters, false);
    }
    // ...
}


// 3. fattn: kv split came from occupancy, 1q vs 2q kernel diff. sneaky af, only past kv 384
fattn_kernel_t occupancy_kernel = nullptr;
if (cols_per_block > 1 && ggml_cuda_batch_invariant()) {
    occupancy_kernel = flash_attn_ext_vec<D, 1, type_K, type_V, use_logit_softcap>;
}
launch_fattn<D, cols_per_block, 1>(ctx, dst, fattn_kernel, nwarps, nbytes_shared, D,
                                   need_f16_K, need_f16_V, false, WARP_SIZE, occupancy_kernel);


// 208/208 runs token-exact, max logit diff 0.000000. ngl it slaps
