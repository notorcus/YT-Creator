import csv, os
from lxml import etree as ET

def ttf(timestamp, frameRate):
    components = timestamp.split(':')
    hours = int(components[0])
    minutes = int(components[1])
    seconds = int(components[2])
    frames = int(components[3])
    
    frames = (hours * 3600 + minutes * 60 + seconds) * frameRate + frames
    return frames

def generate_xml(sequence_name, videoPath, cutstampPath, outputPath, sequence_timebase=30, frameRate=30):

    sequence_ntsc = "FALSE"
    NTSC = "FALSE"

    strPoint = 0
    endPoint = 0

    fileName = "podcast"
    # filePath = r"c:\Users\Akshat Kumar\Videos\David Goggins - How To Get Up Early Every Day [Wnsz6xounv4].mp4"

    # Read CSV file and extract data
    data = []
    with open(cutstampPath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            data.append(row)

    root = ET.Element("xmeml")
    root.set("version", "5")

    sequence = ET.SubElement(root, "sequence")
    sequence.set("id", "sequence-1")

    ET.SubElement(sequence, "name").text = sequence_name
    # Duration of the sequence will be calculated based on clip durations
    sequence_duration = ET.SubElement(sequence, "duration")
    rate = ET.SubElement(sequence, "rate")
    ET.SubElement(rate, "ntsc").text = sequence_ntsc
    ET.SubElement(rate, "timebase").text = str(sequence_timebase)

    ET.SubElement(sequence, "in").text = "-1"
    ET.SubElement(sequence, "out").text = "-1"

    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    video_track = ET.SubElement(video, "track")
    audio = ET.SubElement(media, "audio")  # Create audio node under media
    audio_track = ET.SubElement(audio, "track")  # Create track node under audio

    total_duration = 0
    for i, item in enumerate(data):
        n = i+1
        inPoint = ttf(item[0], sequence_timebase)
        outPoint = ttf(item[1], sequence_timebase)
        duration = (outPoint - inPoint)

        total_duration += duration

        strPoint = endPoint
        endPoint += duration

        # Create audio clipitem
        audio_clipitem = ET.SubElement(audio_track, "clipitem")
        audio_clipitem.set("id", f"clipitem-{n}-audio")
        audio_clipitem.set("premiereChannelType", "stereo")

        # Create child elements of audio clipitem
        ET.SubElement(audio_clipitem, "name").text = f"clipitem-{n}-audio"
        ET.SubElement(audio_clipitem, "duration").text = str(duration)
        rate = ET.SubElement(audio_clipitem, "rate")
        ET.SubElement(rate, "ntsc").text = NTSC
        ET.SubElement(rate, "timebase").text = str(frameRate)
        ET.SubElement(audio_clipitem, "start").text = str(strPoint)
        ET.SubElement(audio_clipitem, "end").text = str(endPoint)
        ET.SubElement(audio_clipitem, "in").text = str(inPoint)
        ET.SubElement(audio_clipitem, "out").text = str(outPoint)
        ET.SubElement(audio_clipitem, "enabled").text = "TRUE"

        file = ET.SubElement(audio_clipitem, "file")
        file.set("id", fileName)

        sourcetrack = ET.SubElement(audio_clipitem, "sourcetrack")
        ET.SubElement(sourcetrack, "mediatype").text = "audio"
        ET.SubElement(sourcetrack, "trackindex").text = "1"

        link1 = ET.SubElement(audio_clipitem, "link")
        ET.SubElement(link1, "linkclipref").text = f"clipitem-{n}"
        ET.SubElement(link1, "mediatype").text = "video"
        ET.SubElement(link1, "trackindex").text = "1"
        ET.SubElement(link1, "clipindex").text = str(n)

        link2 = ET.SubElement(audio_clipitem, "link")
        ET.SubElement(link2, "linkclipref").text = f"clipitem-{n}-audio"
        ET.SubElement(link2, "mediatype").text = "audio"
        ET.SubElement(link2, "trackindex").text = "1"
        ET.SubElement(link2, "clipindex").text = str(n)

        # Create video clipitem
        clipitem = ET.SubElement(video_track, "clipitem")  # Changed from 'root' to 'video_track'
        clipitem.set("id", f"clipitem-{n}")

        # Create child elements of video clipitem
        ET.SubElement(clipitem, "name").text = f"clipitem-{n}"
        ET.SubElement(clipitem, "duration").text = str(duration)
        
        rate = ET.SubElement(clipitem, "rate")
        ET.SubElement(rate, "ntsc").text = NTSC
        ET.SubElement(rate, "timebase").text = str(frameRate)

        ET.SubElement(clipitem, "start").text = str(strPoint)
        ET.SubElement(clipitem, "end").text = str(endPoint)
        ET.SubElement(clipitem, "in").text = str(inPoint)
        ET.SubElement(clipitem, "out").text = str(outPoint)

        file = ET.SubElement(clipitem, "file")
        file.set("id", fileName)
        ET.SubElement(file, "name").text = fileName
        ET.SubElement(file, "pathurl").text = videoPath

        media = ET.SubElement(file, "media")

        video = ET.SubElement(media, "video")
        video_rate = ET.SubElement(video, "rate")
        ET.SubElement(video_rate, "timebase").text = str(frameRate)
        ET.SubElement(video_rate, "ntsc").text = NTSC
        ET.SubElement(video, "duration").text = str(duration)

        audio = ET.SubElement(media, "audio")
        ET.SubElement(audio, "channelcount").text = "2"

        link1 = ET.SubElement(clipitem, "link")
        ET.SubElement(link1, "linkclipref").text = f"clipitem-{n}"
        ET.SubElement(link1, "mediatype").text = "video"
        ET.SubElement(link1, "trackindex").text = "1"
        ET.SubElement(link1, "clipindex").text = str(n)

        link2 = ET.SubElement(clipitem, "link")
        ET.SubElement(link2, "linkclipref").text = f"clipitem-{n}-audio"
        ET.SubElement(link2, "mediatype").text = "audio"
        ET.SubElement(link2, "trackindex").text = "1"
        ET.SubElement(link2, "clipindex").text = str(n)

    # After all clipitems have been processed
    sequence_duration.text = str(total_duration)

    # Use lxml.etree.Element to create a format node
    format_node = ET.Element("format")
    samplecharacteristics = ET.SubElement(format_node, "samplecharacteristics")
    ET.SubElement(samplecharacteristics, "width").text = "1920"
    ET.SubElement(samplecharacteristics, "height").text = "1080"
    ET.SubElement(samplecharacteristics, "anamorphic").text = "FALSE"
    ET.SubElement(samplecharacteristics, "pixelaspectratio").text = "square"
    ET.SubElement(samplecharacteristics, "fielddominance").text = "none"
    rate = ET.SubElement(samplecharacteristics, "rate")
    ET.SubElement(rate, "timebase").text = str(sequence_timebase)
    ET.SubElement(rate, "ntsc").text = sequence_ntsc

    # Use lxml.etree.ElementTree to convert root to an ElementTree
    tree = ET.ElementTree(root)
    # Use lxml.etree.ElementTree.xpath to find video node
    video_node = tree.xpath('//video')[0]
    # Use lxml.etree._Element.insert to insert format node as the last child of the video node
    video_node.insert(len(video_node), format_node)

    xml_string = ET.tostring(root, pretty_print=True)

    # Save pretty printed XML to file
    with open(outputPath, "w") as f:
        f.write(xml_string.decode())

def generate_all_xml(name, videoPath, cutstamp_folder, xml_folder):
    files = os.listdir(cutstamp_folder)

    for i in range(1, len(files) + 1):
        generate_xml(
            name,
            videoPath,
            os.path.join(cutstamp_folder, f"short_{i}.csv"),
            os.path.join(xml_folder, f"short_{i}.xml")
        )
    
    print("XML(s) Created")

if __name__ == "__main__":
    for i in range(1, 14):
        generate_xml("Hormozi", r"projects\Thomass_test\input\Thomass_test.mp4", fr"projects\Thomass_test\intermediate\cutstamps\short_{i}.csv", fr"projects\Thomass_test\intermediate\xml\Short_{i}.xml")
    print("XML Created")