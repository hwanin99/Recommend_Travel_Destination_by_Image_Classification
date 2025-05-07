import os
import glob
import shutil
import time

class Make_Dataset_Dir():
    def __init__(self,
                modes=['train','valid'],
                move_option='move',
                class_names=os.listdir('./dataset'),
                train_split_ratio=7):
                    
        self.modes = modes
        self.move_option = move_option
        self.class_names = class_names 
        self.train_split_ratio = train_split_ratio


    def mk_dir(self):
        ''' mode 디렉토리 만들고 내부에 클래스 디렉토리 만들기 '''
        for mode in self.modes:
            for class_name in self.class_names:
                os.makedirs(f'./{mode}/{class_name}',exist_ok=True)

    
    def move_img(self):
        ''' 클래스 디렉토리로 split해서 옮기기 '''
        for class_name in self.class_names:
            original_path = sorted(glob.glob(f'./dataset/{class_name}/*.jpg')) #Japan, P, V, T, T
            total_num = len(original_path)
            train_num = int(total_num * (self.train_split_ratio/10))

            train = original_path[:train_num]
            valid = original_path[train_num:]

            if self.move_option == 'copy':
                for i,train_path in enumerate(train):
                    shutil.copyfile(train_path,f'./{self.modes[0]}/{class_name}/{class_name}_{i}.jpg')
                for i,valid_path in enumerate(valid):
                    shutil.copyfile(valid_path,f'./{self.modes[1]}/{class_name}/{class_name}_{i}.jpg')

            elif self.move_option == 'move':
                for i,train_path in enumerate(train):
                    shutil.move(train_path,f'./{self.modes[0]}/{class_name}/{class_name}_{i}.jpg')
                for i,valid_path in enumerate(valid):
                    shutil.move(valid_path,f'./{self.modes[1]}/{class_name}/{class_name}_{i}.jpg')

    
    def check(self):
        for mode in self.modes:
            for class_name in self.class_names:
                print(f"{mode}의 {class_name} 이미지: {len(os.listdir(f'./{mode}/{class_name}'))}장")

    
    def run(self):
        start = time.time()
        self.mk_dir()
        self.move_img()
        print(f'총 소요시간: {round(time.time()-start,5)}초')
        print('---------------------------------')
        self.check()
