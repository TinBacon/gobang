import matplotlib.pyplot as plt
import numpy as np
import time


class GoBang:

    def __init__(self):

        self.RATIO = 1                                                                          # >1: attack, <1: defend
        self.DEPTH = 2                                                                          # search depth
        self.COLUMN = 15                                                                        # checkboard column
        self.ROW = 15                                                                           # checkboard row

        self.pieces_ai = []                                                                     # AI pieces
        self.pieces_my = []                                                                     # human pieces
        self.pieces_all = []                                                                    # all pieces
        self.next = [-1, -1]                                                                    # next pice of ai
        self.checkerboard = [(i, j) for i in range(self.COLUMN+1) for j in range(self.ROW+1)]   # checkerboard
        
        self.SHAPE_SCORE = [(50,       (0, 1, 1, 0, 0)),                                        # evaluate score
                            (50,       (0, 0, 1, 1, 0)),
                            (500,      (1, 1, 1, 0, 0)),
                            (500,      (1, 1, 0, 1, 0)),
                            (500,      (0, 1, 1, 1, 0)),
                            (500,      (0, 1, 1, 0, 1, 0)),
                            (500,      (0, 1, 0, 1, 1, 0)),
                            (500,      (0, 0, 1, 1, 1)),
                            (5000,     (1, 1, 1, 1, 0)),
                            (5000,     (1, 1, 1, 0, 1)),
                            (5000,     (1, 1, 0, 1, 1)),
                            (5000,     (1, 0, 1, 1, 1)),
                            (5000,     (0, 1, 1, 1, 1)),
                            (50000,    (0, 1, 1, 1, 1, 0)),
                            (99999999, (1, 1, 1, 1, 1))]

        plt.ion()
        plt.figure('checkboard')
        plt.xlim((-1, self.COLUMN+1))
        plt.ylim((-1, self.ROW+1))
        plt.xticks(np.arange(0, self.COLUMN+1))
        plt.yticks(np.arange(0, self.ROW+1))
        plt.grid(True)
        self.draw()


    def run(self):
        
        # my turn
        self.my_turn()
        # self.my_ai_turn()
        self.pieces_my.append(self.next_my)
        self.pieces_all.append(self.next_my)
        self.draw(False)

        if self.win(self.pieces_my):
            print("YOU WIN")
            return True

        # ai's turn
        self.ai_turn()
        self.pieces_ai.append(tuple(self.next_ai))
        self.pieces_all.append(tuple(self.next_ai))
        self.draw(True)

        if self.win(self.pieces_ai):
            print("YOU LOSE")
            return True
        
        return False


    def my_turn(self):

        while True:
            self.next_my = plt.ginput(1, 999999999)[0]
            self.next_my = tuple(round(c) for c in self.next_my)
            if not (self.next_my in self.pieces_all):
                break

    
    def my_ai_turn(self):

        plt.ginput(1, 99999999)
        if len(self.pieces_my):
            self.cut_count = 0
            self.search_count = 0
            start = time.time()

            # search with negative max and alpha beta pruning
            score = self.search(True, self.DEPTH, -99999999, 99999999)
            score = -score if self.DEPTH%2 else score

            print("piece {:2} | search {:6} times | prune {:6} times | score: {:12} | time: {:.1f}s".format(len(self.pieces_my), self.cut_count, self.search_count, score, time.time()-start))

            self.next_my = tuple(self.next)
        else:
            self.next_my = (self.ROW//2, self.COLUMN//2)


    def ai_turn(self):

        self.cut_count = 0
        self.search_count = 0
        start = time.time()

        # search with negative max and alpha beta pruning
        score = self.search(True, self.DEPTH, -99999999, 99999999)
        score = -score if self.DEPTH%2 else score

        print("piece {:2} | search {:6} times | prune {:6} times | score: {:12} | time: {:.1f}s".format(len(self.pieces_ai), self.cut_count, self.search_count, score, time.time()-start))

        self.next_ai = tuple(self.next)


    def search(self, is_ai, depth, alpha, beta):

        # stop boundary
        if self.win(self.pieces_ai) or self.win(self.pieces_my) or depth == 0:
            return self.evaluation(is_ai)

        # get candidate position
        blank_list = list(set(self.checkerboard).difference(set(self.pieces_all)))
        self.order(blank_list)

        # traverse candidate
        for next_step in blank_list:

            self.search_count += 1

            # only search the position which has neighbor
            if not self.has_neighbor(next_step):
                continue
            
            # search in next depth
            self.pieces_all.append(next_step)
            if is_ai:
                self.pieces_ai.append(next_step)
                value = -self.search(not is_ai, depth-1, -beta, -alpha)
                self.pieces_ai.remove(next_step)
            else:
                self.pieces_my.append(next_step)
                value = -self.search(not is_ai, depth-1, -beta, -alpha)
                self.pieces_my.remove(next_step)
            self.pieces_all.remove(next_step)

            
            if value > alpha:
                
                # first layer
                if depth == self.DEPTH:
                    self.next[0] = next_step[0]
                    self.next[1] = next_step[1]
                
                # pruning
                if value >= beta:
                    self.cut_count += 1
                    return beta

                alpha = value
            

        return alpha


    def order(self, blank_list):

        # near position has higher order
        last_x, last_y = self.pieces_all[-1]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (last_x + i, last_y + j) in blank_list:
                    blank_list.remove((last_x + i, last_y + j))
                    blank_list.insert(0, (last_x + i, last_y + j))


    def has_neighbor(self, pt):

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (pt[0] + i, pt[1]+j) in self.pieces_all:
                    return True
        return False


    def evaluation(self, is_ai):

        my_list = self.pieces_ai if is_ai else self.pieces_my
        enemy_list = self.pieces_my if is_ai else self.pieces_ai

        # my score
        score_all_arr = []
        my_score = 0
        for x, y in my_list:
            my_score += self.calc_score(x, y, 0, 1, enemy_list, my_list, score_all_arr) \
                + self.calc_score(x, y, 1, 0, enemy_list, my_list, score_all_arr) \
                + self.calc_score(x, y, 1, 1, enemy_list, my_list, score_all_arr) \
                + self.calc_score(x, y, -1, 1, enemy_list, my_list, score_all_arr)

        # ai score
        score_all_arr_enemy = []
        enemy_score = 0
        for x, y in enemy_list:
            enemy_score += self.calc_score(x, y, 0, 1, my_list, enemy_list, score_all_arr_enemy) \
                + self.calc_score(x, y, 1, 0, my_list, enemy_list, score_all_arr_enemy) \
                + self.calc_score(x, y, 1, 1, my_list, enemy_list, score_all_arr_enemy) \
                + self.calc_score(x, y, -1, 1, my_list, enemy_list, score_all_arr_enemy)

        total_score = my_score - enemy_score*self.RATIO*0.1

        return total_score


    def calc_score(self, x, y, x_direct, y_direct, enemy_list, my_list, score_all_arr):
        
        # skip the score shape has saved
        for item in score_all_arr:
            for pt in item[1]:
                if x == pt[0] and y == pt[1] and x_direct == item[2][0] and y_direct == item[2][1]:
                    return 0

        # search the max score shape on left and right
        max_score_shape = (0, None)
        for offset in range(-5, 1):
            
            pos = []
            for i in range(0, 6):
                if x + (i + offset) * x_direct < 0 or x + (i + offset) * x_direct > self.COLUMN \
                        or y + (i + offset) * y_direct < 0 or y + (i + offset) * y_direct > self.ROW \
                        or (x + (i + offset) * x_direct, y + (i + offset) * y_direct) in enemy_list:
                    pos.append(2)
                elif (x + (i + offset) * x_direct, y + (i + offset) * y_direct) in my_list:
                    pos.append(1)
                else:
                    pos.append(0)
            tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
            tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])
            
            # every shape and score in the model
            for (score, shape) in self.SHAPE_SCORE:
                if tmp_shap5 == shape or tmp_shap6 == shape:
                    # get the max score
                    if score > max_score_shape[0]:
                        max_score_shape = (score, ((x + (0+offset) * x_direct, y + (0+offset) * y_direct),
                                                   (x + (1+offset) * x_direct, y + (1+offset) * y_direct),
                                                   (x + (2+offset) * x_direct, y + (2+offset) * y_direct),
                                                   (x + (3+offset) * x_direct, y + (3+offset) * y_direct),
                                                   (x + (4+offset) * x_direct, y + (4+offset) * y_direct)), (x_direct, y_direct))
        
        # if intersect, add scores
        add_score = 0 
        if max_score_shape[1] is not None:
            for item in score_all_arr:
                for pt1 in item[1]:
                    for pt2 in max_score_shape[1]:
                        if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                            add_score += item[0] + max_score_shape[0]

            score_all_arr.append(max_score_shape)

        return add_score + max_score_shape[0]


    def win(self, list):

        for x in range(self.COLUMN+1):
            for y in range(self.ROW+1):
                # check four directions
                if (y < self.ROW - 3 and (x, y) in list and (x, y + 1) in list and (x, y + 2) in list and (x, y + 3) in list and (x, y + 4) in list) \
                        or (x < self.COLUMN - 3 and (x, y) in list and (x + 1, y) in list and (x + 2, y) in list and (x + 3, y) in list and (x + 4, y) in list) \
                        or (x < self.COLUMN - 3 and y < self.ROW - 3 and (x, y) in list and (x + 1, y + 1) in list and (x + 2, y + 2) in list and (x + 3, y + 3) in list and (x + 4, y + 4) in list) \
                        or (x < self.COLUMN - 3 and y > 3 and (x, y) in list and (x + 1, y - 1) in list and (x + 2, y - 2) in list and (x + 3, y - 3) in list and (x + 4, y - 4) in list):
                    return True
        
        return False


    def draw(self, is_ai=False):

        # draw checkboard
        ax = plt.gca()
        ax.set_xlabel('x')
        ax.set_ylabel('y')

        # draw piece
        n = len(self.pieces_ai) if is_ai else len(self.pieces_my)
        if n<10:
            offset_x = 0.08
        else:
            offset_x = 0.22
        # ai turn
        if is_ai:
            ax.scatter(self.next_ai[0], self.next_ai[1], c='r', s=250, alpha=0.5)
            plt.text(self.next_ai[0]-offset_x, self.next_ai[1]-0.15, str(n), color='white', size=10)
            ax.scatter(self.next_my[0], self.next_my[1], c='b', s=250)
        # my turn
        elif n>0:
            ax.scatter(self.next_my[0], self.next_my[1], c='b', s=250, alpha=0.5)
            plt.text(self.next_my[0]-offset_x, self.next_my[1]-0.15, str(n), color='white', size=10)

            if n>1:
                ax.scatter(self.next_ai[0], self.next_ai[1], c='r', s=250)

        plt.show()


gobang = GoBang()
while True:

    end = gobang.run()

    if end:
        break

plt.savefig('{}.jpg'.format(time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())))
plt.ginput(1, 999999999)