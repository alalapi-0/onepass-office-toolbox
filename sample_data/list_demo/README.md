# list_demo

用于测试 `list_tools` 中的 Excel/CSV 列表处理工具。

示例命令：

```bash
# 从 csv 文件生成文件名列表
python -m onepass_office_toolbox.cli list excel-to-filenames \
    --input sample_data/list_demo/demo_filenames.csv \
    --column filename \
    --output sample_data/list_demo/filename_list.txt

# 对文件名列做去重分析
python -m onepass_office_toolbox.cli list dedup-filename-column \
    --input sample_data/list_demo/demo_filenames.csv \
    --column filename \
    --unique-output sample_data/list_demo/unique_filenames.txt \
    --duplicates-output sample_data/list_demo/duplicate_filenames.txt
```
