from PIC import bmp2pic,pic2bmp,read_pic_info,read_bmp_info

# 伪彩色图
bmp_file_path='./lena.bmp'
pic_file_path='./lena.pic'
# bmp to pic
bmp2pic(bmp_file_path,pic_file_path)

# pic to bmp
bmp_file_path_new='./lena_new.bmp'
pic2bmp(pic_file_path,bmp_file_path_new)

# information
read_bmp_info(bmp_file_path)
read_pic_info(pic_file_path)

# 真彩图
bmp_file_path2='./Elaina.bmp'
pic_file_path2='./Elaina.pic'
# bmp to pic
bmp2pic(bmp_file_path2,pic_file_path2)


# pic to bmp
bmp_file_path2_new='./Elaina_new.bmp'
pic2bmp(pic_file_path2,bmp_file_path2_new)

# information
read_bmp_info(bmp_file_path2)
read_pic_info(pic_file_path2)
read_bmp_info(bmp_file_path2_new)