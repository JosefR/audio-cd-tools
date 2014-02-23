#!/usr/bin/env python
import argparse
import subprocess
import os
import glob

def gettag(tag, filename):
    proc = subprocess.Popen(["metaflac", "--no-utf8-convert", 
        "--show-tag=" + tag, filename], stdout=subprocess.PIPE)
    out = proc.communicate()[0].rstrip()
    remove = len(out.split("=")[0]) + 1
    return out[remove:]

def decode_flac(flacfile, wavfile):
    proc = subprocess.Popen(["flac", "-d", "-f", "-o", wavfile, flacfile])
    proc.wait()
    return 0 if proc.returncode == 0 else 1

def encode_mp3(wavfile, mp3file):
    proc = subprocess.Popen(["lame", "-h", "-V0", wavfile, mp3file])
    proc.wait()
    return 0 if proc.returncode == 0 else 1

def tag_mp3(mp3file, metadata):
    proc = subprocess.Popen(["eyeD3", 
        "-t", metadata["title"], 
        "-n", metadata["tracknumber"], 
        "-a", metadata["artist"], 
        "-A", metadata["album"], 
        "-G", metadata["genre"], 
        "-Y", metadata["year"], 
        "-A", metadata["album"], 
        "--add-image=" + metadata["cover"] + ":FRONT_COVER", 
        mp3file])
    proc.wait()
    return 0 if proc.returncode == 0 else 1


# parse command line arguments
parser = argparse.ArgumentParser(description='Convert flac files to mp3');
parser.add_argument('-i', metavar='input directory')
parser.add_argument('-o', metavar='output directory')
args = parser.parse_args()
if args.i:
    indir = args.i
else:
    indir="."
if args.o:
    outdir = args.o
else:
    outdir="."
print("read flac files from " + indir + "; results will be written to " + 
    outdir)

# convert and flag each file in directory 
for filepath in os.listdir(indir):
    print "path:" + filepath
    if not filepath.endswith(".flac"):
        continue
    basename = os.path.basename(filepath)[0:-5]
    flacname = indir + "/" + basename + ".flac"
    wavname = outdir + "/" + basename + ".wav"
    mp3name = outdir + "/" + basename + ".mp3"
    print "transcode: " + flacname
    metadata = {
        "title" : gettag("TITLE", flacname),
        "tracknumber" : gettag("TRACKNUMBER", flacname),
        "artist" : gettag("ARTIST", flacname),
        "album" : gettag("ALBUM", flacname),
        "genre" : gettag("GENRE", flacname),
        "year" : gettag("DATE", flacname)
    }
    if os.path.isfile("cover.png"):
        metadata["cover"] = "cover.png"
    elif os.path.isfile("cover.jpg"):
        metadata["cover"] = "cover.jpg"
    else:
        metadata["cover"] = ""
    
    print metadata
 
    if decode_flac(flacname, wavname):
        print "decoding flac failed"
        exit(1)

    if encode_mp3(wavname, mp3name):
        print "encoding mp3 failed"
        exit(1)

    if tag_mp3(mp3name, metadata):
        print "tagging mp3 failed"
        exit(1)

    os.remove(wavname);

print "finished"
