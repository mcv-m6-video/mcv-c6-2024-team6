import utils
import cv2

if __name__ == "__main__":

    video_path = '/ghome/group07/test/W3/task_2/train/S04/c028/vdo.avi'

    gray_frames, color_frames = utils.read_video(video_path)

    for i in range(len(gray_frames)):
        out_path_gray = "/ghome/group07/test/W3/task_2/frame_dataset/S04/c028/gray/"+str(i)+".png"
        out_path_color = "/ghome/group07/test/W3/task_2/frame_dataset/S04/c028/color/"+str(i)+".png"

        print(str(i))
        
        cv2.imwrite(out_path_gray, gray_frames[i])
        # COLORED IMAGES FROM BGR TO RGB
        cv2.imwrite(out_path_color, color_frames[i][:, :, ::-1])

