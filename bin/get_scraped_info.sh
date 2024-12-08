cd C:\Users\y3-hara\program_files\program\lowcode-scraper

python .\src\lowcode_scraper.py \
    --browser_binary_path "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" \
    --driver_path "C:\Users\y3-hara\program_files\program\lowcode-scraper\driver\msedgedriver.exe" \
    --data_dir "C:\Users\y3-hara\program_files\program\lowcode-scraper\data" \
    --base_dataset_name "base_reviews" \
    --scraped_dataset_name "airline_reviews" \
    --content_layout "multiple" \
    --multiple_top_k 5 \
    --csv_encoding_format "utf-8-sig"