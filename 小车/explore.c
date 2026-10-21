#include <stdio.h>

#define ROWS 8
#define COLS 10

char map[ROWS][COLS] = {          /* 真实环境（小车看不见全部） */
    "##########",
    "#S.....#C#",
    "#.#.##.#.#",
    "#.#....#.#",
    "#.####.#.#",
    "#....#...#",
    "#C...#...#",
    "##########"
};

char known[ROWS][COLS];           /* 小车脑中的地图：'?' = 没见过 */
int  visits[ROWS][COLS];          /* 每格到过的次数 */
int carX = 1, carY = 1;           /* 从 S 出发 */
int dx[4] = {0, 0, -1, 1};        /* 四个方向：左右上下 */
int dy[4] = {-1, 1, 0, 0};

void sense(void) {                /* 虚拟传感器：只认识周围 3x3 */
    for (int r = carY - 1; r <= carY + 1; r++)
        for (int c = carX - 1; c <= carX + 1; c++)
            if (r >= 0 && r < ROWS && c >= 0 && c < COLS)
                known[r][c] = map[r][c];
}

int allSeen(void) {               /* 环境是否已经学完 */
    for (int r = 0; r < ROWS; r++)
        for (int c = 0; c < COLS; c++)
            if (map[r][c] != '#' && known[r][c] == '?') return 0;
    return 1;
}

int main(void) {
    for (int r = 0; r < ROWS; r++)
        for (int c = 0; c < COLS; c++) { known[r][c] = '?'; visits[r][c] = 0; }

    int step;
    for (step = 1; step <= 2000 && !allSeen(); step++) {
        sense();                              /* 感知 */
        int best = -1, bestVis = 99999;       /* 决策：挑到过次数最少的邻格 */
        for (int d = 0; d < 4; d++) {
            int nx = carX + dx[d], ny = carY + dy[d];
            if (known[ny][nx] != '#' && known[ny][nx] != '?')
                if (visits[ny][nx] < bestVis) { bestVis = visits[ny][nx]; best = d; }
        }
        if (best < 0) break;
        carX += dx[best]; carY += dy[best];   /* 执行 */
        visits[carY][carX]++;
    }

    printf("=== xiao che nao zhong de di tu (? = mei jian guo) zou le %d bu ===\n", step - 1);
    for (int r = 0; r < ROWS; r++) {
        for (int c = 0; c < COLS; c++) printf("%c", known[r][c]);
        printf("\n");
    }
    return 0;
}