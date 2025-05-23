import cv2
import numpy as np
import matplotlib.pyplot as plt
 
img_man = cv2.imread('image/OIP.jpg',0) #直接读为灰度图像
plt.subplot(121),plt.imshow(img_man,'gray'),plt.title('origial')
plt.xticks([]),plt.yticks([])
#--------------------------------
rows, cols = img_man.shape
center_row = rows // 2
center_col = cols // 2
mask1 = np.ones(img_man.shape, np.uint8)
mask1[center_row-8:center_row+8, center_col-8:center_col+8] = 0
mask2 = np.zeros(img_man.shape, np.uint8)
mask2[center_row-80:center_row+80, center_col-80:center_col+80] = 1
mask = mask1*mask2
#--------------------------------
f1 = np.fft.fft2(img_man)
f1shift = np.fft.fftshift(f1)
f1shift = f1shift*mask
f2shift = np.fft.ifftshift(f1shift) #对新的进行逆变换
img_new = np.fft.ifft2(f2shift)
#出来的是复数，无法显示
img_new = np.abs(img_new)
#调整大小范围便于显示
img_new = (img_new-np.amin(img_new))/(np.amax(img_new)-np.amin(img_new))
plt.subplot(122),plt.imshow(img_new,'gray')
plt.xticks([]),plt.yticks([])
plt.show()