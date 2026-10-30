# 等预算对照

每host-source10行不是相同TOTAL预算。P0基准同一975输入供全部方法；native控制只去主机/来源标题而保留全部事件/续行。records40以来源轮转选择最多40条原生记录，tokens2048以来源轮转最多2048个非空白片段，并保存最后一行前缀hash。这里Token为明确regex代理，不是某LLM tokenizer Token；不能推算模型调用成本。

相同view各算法看到同样sources内容，不让新机制多拿日志。P2-Full只表示获准filtered完整步骤，非完整攻击历史。

| Method | Protocol | View | N | Top1% | Top5% | Top10% | StepMacroTop10% | P@5 | R@5 | MRR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BM25 | P0 | native | 975 | 6.05 | 15.79 | 23.69 | 23.69 | 0.0316 | 0.1330 | 0.1055 |
| BM25 | P0 | records40 | 975 | 5.85 | 15.79 | 22.97 | 22.97 | 0.0316 | 0.1330 | 0.1021 |
| BM25 | P0 | tokens2048 | 975 | 6.05 | 15.79 | 23.69 | 23.69 | 0.0316 | 0.1330 | 0.1055 |
| CharacterNgramTFIDF | P0 | native | 975 | 8.62 | 16.31 | 27.79 | 27.79 | 0.0326 | 0.1462 | 0.1294 |
| CharacterNgramTFIDF | P0 | records40 | 975 | 8.21 | 16.00 | 27.59 | 27.59 | 0.0320 | 0.1431 | 0.1269 |
| CharacterNgramTFIDF | P0 | tokens2048 | 975 | 8.62 | 16.31 | 27.79 | 27.79 | 0.0326 | 0.1462 | 0.1294 |
| WordCharacterHybrid | P0 | native | 975 | 5.54 | 16.92 | 25.54 | 25.54 | 0.0338 | 0.1533 | 0.1063 |
| WordCharacterHybrid | P0 | records40 | 975 | 5.54 | 16.31 | 25.03 | 25.03 | 0.0326 | 0.1472 | 0.1041 |
| WordCharacterHybrid | P0 | tokens2048 | 975 | 5.54 | 16.92 | 25.54 | 25.54 | 0.0338 | 0.1533 | 0.1063 |
| TFIDF | P0 | native | 975 | 5.95 | 17.33 | 22.67 | 22.67 | 0.0347 | 0.1517 | 0.1007 |
| TFIDF | P0 | records40 | 975 | 5.95 | 16.92 | 22.67 | 22.67 | 0.0338 | 0.1515 | 0.0992 |
| TFIDF | P0 | tokens2048 | 975 | 5.95 | 17.33 | 22.67 | 22.67 | 0.0347 | 0.1517 | 0.1007 |
| SourceWiseBM25_Max | P0 | native | 975 | 3.18 | 14.56 | 25.44 | 25.44 | 0.0302 | 0.1216 | 0.0849 |
| SourceWiseBM25_Mean | P0 | native | 975 | 6.46 | 17.23 | 24.10 | 24.10 | 0.0345 | 0.1448 | 0.1116 |
| SourceWiseBM25_RRF | P0 | native | 975 | 6.97 | 14.77 | 22.87 | 22.87 | 0.0295 | 0.1344 | 0.1065 |
| SourceWiseBM25_SourceScoreNormalization | P0 | native | 975 | 6.87 | 17.64 | 24.31 | 24.31 | 0.0353 | 0.1515 | 0.1118 |
| EvidenceLineFusion_NoDiscrimination_bm25 | P0 | native | 975 | 3.49 | 15.79 | 22.67 | 22.67 | 0.0316 | 0.1383 | 0.0827 |
| EvidenceLineFusion_NoLineSelection_bm25 | P0 | native | 975 | 2.56 | 13.74 | 24.41 | 24.41 | 0.0275 | 0.1188 | 0.0790 |
| EvidenceLineFusion_NoSourceCalibration_bm25 | P0 | native | 975 | 3.08 | 15.18 | 22.97 | 22.97 | 0.0304 | 0.1320 | 0.0838 |
| EvidenceLineFusion_bm25 | P0 | native | 975 | 2.67 | 15.28 | 24.21 | 24.21 | 0.0306 | 0.1306 | 0.0813 |
| SourceWiseBM25_Max | P0 | records40 | 975 | 2.67 | 14.46 | 24.62 | 24.62 | 0.0299 | 0.1244 | 0.0814 |
| SourceWiseBM25_Mean | P0 | records40 | 975 | 6.56 | 17.03 | 23.38 | 23.38 | 0.0341 | 0.1427 | 0.1104 |
| SourceWiseBM25_RRF | P0 | records40 | 975 | 6.97 | 14.56 | 22.87 | 22.87 | 0.0291 | 0.1323 | 0.1061 |
| SourceWiseBM25_SourceScoreNormalization | P0 | records40 | 975 | 6.87 | 16.92 | 24.31 | 24.31 | 0.0338 | 0.1443 | 0.1101 |
| EvidenceLineFusion_NoDiscrimination_bm25 | P0 | records40 | 975 | 3.08 | 15.90 | 22.67 | 22.67 | 0.0318 | 0.1386 | 0.0804 |
| EvidenceLineFusion_NoLineSelection_bm25 | P0 | records40 | 975 | 2.56 | 14.26 | 24.41 | 24.41 | 0.0285 | 0.1239 | 0.0790 |
| EvidenceLineFusion_NoSourceCalibration_bm25 | P0 | records40 | 975 | 2.56 | 14.46 | 22.97 | 22.97 | 0.0289 | 0.1248 | 0.0802 |
| EvidenceLineFusion_bm25 | P0 | records40 | 975 | 2.67 | 15.28 | 23.69 | 23.69 | 0.0306 | 0.1306 | 0.0804 |
| SourceWiseBM25_Max | P0 | tokens2048 | 975 | 3.18 | 14.56 | 25.44 | 25.44 | 0.0302 | 0.1216 | 0.0849 |
| SourceWiseBM25_Mean | P0 | tokens2048 | 975 | 6.46 | 17.23 | 24.10 | 24.10 | 0.0345 | 0.1448 | 0.1116 |
| SourceWiseBM25_RRF | P0 | tokens2048 | 975 | 6.97 | 14.77 | 22.87 | 22.87 | 0.0295 | 0.1344 | 0.1065 |
| SourceWiseBM25_SourceScoreNormalization | P0 | tokens2048 | 975 | 6.87 | 17.64 | 24.31 | 24.31 | 0.0353 | 0.1515 | 0.1118 |
| EvidenceLineFusion_NoDiscrimination_bm25 | P0 | tokens2048 | 975 | 3.49 | 15.79 | 22.67 | 22.67 | 0.0316 | 0.1383 | 0.0827 |
| EvidenceLineFusion_NoLineSelection_bm25 | P0 | tokens2048 | 975 | 2.56 | 13.74 | 24.41 | 24.41 | 0.0275 | 0.1188 | 0.0790 |
| EvidenceLineFusion_NoSourceCalibration_bm25 | P0 | tokens2048 | 975 | 3.08 | 15.18 | 22.97 | 22.97 | 0.0304 | 0.1320 | 0.0838 |
| EvidenceLineFusion_bm25 | P0 | tokens2048 | 975 | 2.67 | 15.28 | 24.21 | 24.21 | 0.0306 | 0.1306 | 0.0813 |
