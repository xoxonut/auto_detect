import time
import subprocess
from pathlib import Path
from tqdm import tqdm


ewf_src_file = "/home/sans/PT01.E01"
ewf_dst_dir = "/mnt/ewf"
instance_file = "/home/sans/test"

# unit of chunk size is byte
def read_chunks(filename,chunk_size=16): 
	with open(filename,"rb") as f:
		while True:
			chunk = f.read(chunk_size)
			if not chunk:
				break
			yield chunk


def mount_ewf(ewf_src_file,ewf_dst_dir):
    if not Path(ewf_dst_dir).exists():
        subprocess.run(["sudo","mkdir",ewf_dst_dir],capture_output=True)

    subprocess.run(["sudo","ewfmount",ewf_src_file,ewf_dst_dir],capture_output=True)
    print(Path(ewf_dst_dir+"/ewf1").exists())



try:
    st = time.time()
    mount_ewf(ewf_src_file,ewf_dst_dir)
    ewf_dst_file = ewf_dst_dir + "/ewf1"
    offsets = []
    # to do : test the way to mount multiple disk images from single ewf file
    byte_sign =  bytes.fromhex("EB 52 90 4E 54 46 53")
    for it,chunk in enumerate(tqdm(read_chunks(ewf_dst_file))):
        if chunk.startswith(byte_sign):
            offsets.append(it*16)
    with open('./a.out','w') as out:
        for offset in offsets:
            try:
                print(offset)
                subprocess.run(["sudo","mount","-o","ro,noload,offset="+str(offset),ewf_dst_file,instance_file],check=True,capture_output=True)
                subprocess.run(["sudo","umount",instance_file],capture_output=True)
                out.writelines(offset)
            except:
                pass
    
finally:
    subprocess.run(["sudo","umount",instance_file],capture_output=True)
    subprocess.run(["sudo","umount",ewf_dst_dir],capture_output=True)
    subprocess.run(["sudo","rm","-r",ewf_dst_dir],capture_output=True)
    print(time.time()-st)
