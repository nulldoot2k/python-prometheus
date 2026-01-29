#!/bin/bash

# Configuration
BASE_URL="http://localhost:8080"
INTERVAL=5  # seconds between requests

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counter
REQUEST_COUNT=0

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Auto Request Script${NC}"
echo -e "${GREEN}Target: $BASE_URL${NC}"
echo -e "${GREEN}Interval: ${INTERVAL}s${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Function to generate random Vietnamese name
generate_random_name() {
    local surnames=("Nguyễn" "Trần" "Lê" "Phạm" "Hoàng" "Phan" "Vũ" "Đặng" "Bùi" "Đỗ" "Hồ" "Ngô" "Dương" "Lý")
    local midnames=("Văn" "Thị" "Minh" "Hữu" "Đức" "Anh" "Hồng" "Quang" "Thu" "Thanh")
    local names=("A" "B" "C" "D" "E" "F" "G" "H" "K" "L" "M" "N" "P" "Q" "T" "V" "X" "Y")
    
    local surname="${surnames[$RANDOM % ${#surnames[@]}]}"
    local midname="${midnames[$RANDOM % ${#midnames[@]}]}"
    local name="${names[$RANDOM % ${#names[@]}]}"
    
    echo "$surname $midname $name"
}

# Function to generate random Vietnamese book title
generate_random_title() {
    local prefixes=("Hành Trình" "Cuộc Chiến" "Truyền Thuyết" "Kỷ Nguyên" "Vương Giả" "Đế Vương" "Huyền Thoại" "Bí Ẩn" "Hồi Ức" "Ký Ức" "Phiêu Lưu" "Thiên Hạ" "Giang Hồ" "Võ Lâm")
    local suffixes=("Phương Đông" "Thần Thoại" "Huyền Bí" "Cổ Đại" "Tương Lai" "Đại Lục" "Thiên Địa" "Vô Song" "Truyền Kỳ" "Bất Diệt" "Vĩnh Hằng" "Tối Cao" "Bất Tử" "Huyền Môn")
    
    local prefix="${prefixes[$RANDOM % ${#prefixes[@]}]}"
    local suffix="${suffixes[$RANDOM % ${#suffixes[@]}]}"
    local number=$((RANDOM % 100 + 1))
    
    # Randomly choose format
    case $((RANDOM % 3)) in
        0) echo "$prefix $suffix" ;;
        1) echo "$prefix $suffix $number" ;;
        2) echo "$suffix $prefix" ;;
    esac
}

# Function to generate random English title
generate_random_english_title() {
    local words=("Legend" "Empire" "Journey" "Chronicles" "Saga" "Quest" "War" "King" "Dragon" "Shadow" "Light" "Dark" "Mystic" "Ancient" "Eternal" "Divine" "Supreme" "Ultimate" "Rising" "Fallen")
    
    local word1="${words[$RANDOM % ${#words[@]}]}"
    local word2="${words[$RANDOM % ${#words[@]}]}"
    
    case $((RANDOM % 3)) in
        0) echo "The $word1 $word2" ;;
        1) echo "$word1 of the $word2" ;;
        2) echo "$word1 and $word2" ;;
    esac
}

# Function to generate random publisher
generate_random_publisher() {
    local publishers=("NXB Kim Đồng" "NXB Trẻ" "NXB Văn Học" "NXB Hội Nhà Văn" "NXB Thanh Niên" "NXB Phụ Nữ" "NXB Lao Động" "NXB Tổng Hợp" "NXB Đại Học Quốc Gia" "NXB Chính Trị" "NXB Giáo Dục" "NXB Tư Pháp")
    
    echo "${publishers[$RANDOM % ${#publishers[@]}]}"
}

# Function to make GET request to home page
request_home() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} GET / - Home page"
    curl -k -s -o /dev/null -w "Status: %{http_code} | Time: %{time_total}s\n" \
        "$BASE_URL/"
}

# Function to get all books
request_get_books() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} GET /books - List all books"
    curl -k -s -o /dev/null -w "Status: %{http_code} | Time: %{time_total}s\n" \
        "$BASE_URL/books"
}

# Function to create a new book
request_create_book() {
    local title=$(generate_random_title)
    local novel_title=$(generate_random_english_title)
    local author=$(generate_random_name)
    local publisher=$(generate_random_publisher)
    
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} POST /books - Create: $title"
    curl -k -s -L -o /dev/null -w "Status: %{http_code} | Time: %{time_total}s\n" \
        -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "title=$title" \
        -d "novel_title=$novel_title" \
        -d "author=$author" \
        -d "publisher=$publisher" \
        "$BASE_URL/books"
}

# Function to get a specific book (if exists)
request_get_book() {
    local book_id=$((1 + $RANDOM % 20))  # Random ID between 1-20
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} GET /books/$book_id - Get book details"
    curl -k -s -o /dev/null -w "Status: %{http_code} | Time: %{time_total}s\n" \
        "$BASE_URL/books/$book_id"
}

# Function to update a book
request_update_book() {
    local book_id=$((1 + $RANDOM % 10))  # Random ID between 1-10
    local title=$(generate_random_title)
    local novel_title=$(generate_random_english_title)
    local author=$(generate_random_name)
    local publisher=$(generate_random_publisher)
    
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} PUT /books/$book_id - Update book"
    curl -k -s -o /dev/null -w "Status: %{http_code} | Time: %{time_total}s\n" \
        -X PUT \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "title=$title" \
        -d "novel_title=$novel_title" \
        -d "author=$author" \
        -d "publisher=$publisher" \
        "$BASE_URL/books/$book_id"
}

# Main loop
while true; do
    REQUEST_COUNT=$((REQUEST_COUNT + 1))
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Request #$REQUEST_COUNT${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Randomly choose which request to make
    case $((RANDOM % 10)) in
        0|1|2)
            # 30% - Home page
            request_home
            ;;
        3|4)
            # 20% - Get all books
            request_get_books
            ;;
        5|6|7)
            # 30% - Create new book
            request_create_book
            ;;
        8|9)
            # 20% - Update book
            request_update_book
            ;;
    esac
    
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Wait before next request
    sleep $INTERVAL
done
