#!/bin/bash

GREEN='\033[1;32m'
RED='\033[1;31m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

declare -A TARGETS=(
    ["01_linear_path.txt"]=6
    ["02_simple_fork.txt"]=6
    ["03_basic_capacity.txt"]=8
    ["01_dead_end_trap.txt"]=15
    ["02_circular_loop.txt"]=20
    ["03_priority_puzzle.txt"]=12
    ["01_maze_nightmare.txt"]=45
    ["02_capacity_hell.txt"]=60
    ["03_ultimate_challenge.txt"]=35
    ["01_the_impossible_dream.txt"]=45
)

MAPS_DIR="$HOME/Downloads/maps"
PASS=0
FAIL=0

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}      🛸 FLY-IN AUTOMATED TESTER 🛸      ${NC}"
echo -e "${BLUE}==========================================${NC}"

for category in easy medium hard challenger; do
    echo -e "\n${YELLOW}▶ ${category^^}${NC}"
    for map_file in "$MAPS_DIR/$category"/*.txt; do
        [ -f "$map_file" ] || continue
        map_name=$(basename "$map_file")
        target=${TARGETS[$map_name]:-999}

        output=$(timeout 30 python3 fly-in.py "$map_file" 2>&1)
        status=$?

        if [ $status -eq 124 ]; then
            echo -e "  [ ${RED}TIMEOUT${NC} ] $map_name"
            ((FAIL++))
            continue
        fi

        if [ $status -ne 0 ]; then
            echo -e "  [ ${RED}CRASH${NC} ] $map_name"
            echo -e "          ↳ $output"
            ((FAIL++))
            continue
        fi

        turns=$(echo "$output" | grep -v '^\s*$' | wc -l | tr -d ' ')

        echo -e "\n${YELLOW}--- Output: $map_name ---${NC}"
        echo "$output"
        echo -e "${YELLOW}----------------------------${NC}"
        if [ "$turns" -le "$target" ]; then
            echo -e "  [ ${GREEN}PASS${NC} ] $map_name → ${turns} turns (target: ≤${target})"
            ((PASS++))
        else
            echo -e "  [ ${RED}FAIL${NC} ] $map_name → ${turns} turns (target: ≤${target})"
            ((FAIL++))
        fi
    done
done

echo -e "\n${BLUE}==========================================${NC}"
echo -e "  ${GREEN}PASS: $PASS${NC} | ${RED}FAIL: $FAIL${NC}"
echo -e "${BLUE}==========================================${NC}"
