# 真实训练成本

[{'method': 'B2', 'configurations': 42, 'updates': 5040, 'epochs_each': 120, 'CPU_seconds_sum': 13.044140999999996, 'wall_seconds_config_sum': 13.862571589183062, 'peak_process_rss_bytes_max': 109543424, 'checkpoint_bytes_sum': 40649823, 'trainable_parameters_min': 114744, 'trainable_parameters_max': 153675}]

B2逐配置时间不含每折共用词表/特征构建；进程RSS为累计峰值，不是每模型增量。CPU头不消耗模型Tokenizer，训练Token为N/A，而非0；视图/更新曝光次数另存收据。GTE原始特征前向的Token成本应与CPU训练单独报告。投影训练不是GTE主干微调。新GPU训练和LoRA始终不得由旧前向权限推定。
