#!/bin/bash

# Configuration
BASE_URL="http://localhost:8080"
INTERVAL=5

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Sample book data for random insertion
declare -a TITLES=("Cuộc Chiến Thần Thoại" "Hành Trình Về Phương Đông" "Kỷ Nguyên Huyền Bí" "Vương Giả Thiên Hạ" "Đế Vương Truyền Kỳ")
declare -a NOVEL_TITLES=("The Mythical War" "Journey to the East" "The Mystic Era" "King of the World" "Emperor's Legend")
declare -a AUTHORS=("Nguyễn Văn A" "Trần Thị B" "Lê Văn C" "Phạm Thị D" "Hoàng Văn E")
declare -a PUBLISHERS=("NXB Kim Đồng" "NXB Trẻ" "NXB Văn Học" "NXB Hội Nhà Văn" "NXB Thanh Niên")

# Counter
REQUEST_COUNT=0

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Auto Request Script${NC}"
echo -e "${GREEN}Target: $BASE_URL${NC}"
echo -e "${GREEN}Interval: ${INTERVAL}s${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Function to get random element from array
get_random() {
    local arr=("$@")
    echo "${arr[$RANDOM % ${#arr[@]}]}"
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
    local title=$(get_random "${TITLES[@]}")
    local novel_title=$(get_random "${NOVEL_TITLES[@]}")
    local author=$(get_random "${AUTHORS[@]}")
    local publisher=$(get_random "${PUBLISHERS[@]}")
    
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
    local title=$(get_random "${TITLES[@]}")
    
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} PUT /books/$book_id - Update book"
    curl -k -s -o /dev/null -w "Status: %{http_code} | Time: %{time_total}s\n" \
        -X PUT \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "title=$title (Updated)" \
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
