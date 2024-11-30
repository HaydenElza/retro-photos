from PIL import Image, ImageDraw, ImageFont
import os, glob


# Parameters
in_path = "input/"
out_path = "output/"
aspect_ratio = 3/4
font = "calculatrix-7.ttf"
font_size = 36


def get_key(file_path):
    filename = os.path.splitext(os.path.basename(file_path))[0]
    int_part = filename.split()[0]
    return int(int_part)

def get_exif(image: Image, index: int) -> dict:
  return image.getexif()[index]

def crop(image: Image, aspect_ratio: float) -> Image:
  
  def trim_height(image: Image, aspect_ratio: float, width: int, height: int) -> Image:
    old_height = height
    height = int(width/aspect_ratio)
    top = int((old_height-height)/2)
    return image, height, top
  
  def trim_width(image: Image, aspect_ratio: float, width: int, height: int) -> Image:
    old_width = width
    width = int(height*aspect_ratio)
    left = int((old_width-width)/2)
    return image, width, left
  
  width, height = image.size
  top,left = 0,0
  
  portrait = height>width
  aspect_ratio = aspect_ratio if portrait else 1/aspect_ratio
  greater_aspect_ratio = round(width/height,2)>round(aspect_ratio,2) if portrait else round(width/height,2)>round(aspect_ratio,2)
  
  
  if portrait:
    if greater_aspect_ratio:
      image, width, left = trim_width(image, aspect_ratio, width, height)
    else:
      image, height, top = trim_height(image, aspect_ratio, width, height)
   
  else:
    if greater_aspect_ratio:
      # image, height, top = trim_height(image, aspect_ratio, width, height)
      image, width, left = trim_width(image, aspect_ratio, width, height)
    else:
      # image, width, left = trim_width(image, aspect_ratio, width, height)
      image, height, top = trim_height(image, aspect_ratio, width, height)
    
  return image.crop((left,top,left+width,top+height))

def add_date(image: Image, font_size: float, font:str=font) -> Image:
  
  # Get date from exif
  year, month, day = get_exif(image, 306).split(' ')[0].split(':')
  date_string = "'{} {} {}".format(year[-2:], month, day)
  
  # Create a drawing object
  draw = ImageDraw.Draw(image)
  
  # Choose a font
  font = ImageFont.truetype(font, font_size)
  
  # Set the text color and position
  text_color = (255, 154, 46)
  text_position = (image.width-(image.height/10), image.height-(image.height/10))
  
  # Draw the text on the image
  draw.text(text_position, date_string, font=font, fill=text_color, anchor='rb')
  
  return image

def rotate(image: Image, landscape:bool=True) -> Image:
  in_landscape = image.width>image.height
  
  if not in_landscape and landscape:
    image = image.rotate(-90, expand=True)
    
  elif in_landscape and not landscape:
    image = image.rotate(90, expand=True)
  
  return image

def resize(image: Image, max_dimension: int) -> Image:
  image_max = max(image.width, image.height)
  
  # Enlarge if needed
  if image_max<max_dimension:
    if image.height>image.width:
      image = image.resize((int(max_dimension*aspect_ratio), max_dimension))
    else:
      image = image.resize((max_dimension, int(max_dimension*aspect_ratio)))

  return image


# Create file list
try:
  file_list = sorted(glob.glob(os.path.join(os.getcwd(),in_path,'*')), key=get_key)
except:
  file_list = glob.glob(os.path.join(os.getcwd(),in_path,'*'))


# Create output directory
if not os.path.isdir(out_path):
  os.mkdir(out_path)

# Iterate through image pairs
for i in range(int(len(file_list)/2)):
  
  # Load image pair
  img1 = Image.open(os.path.join(in_path, file_list[i*2]))
  img2 = Image.open(os.path.join(in_path, file_list[i*2+1]))

  # Crop
  img1 = crop(img1, aspect_ratio)
  img2 = crop(img2, aspect_ratio)
  
  # Ensure landscape orientation
  img1 = rotate(img1)
  img2 = rotate(img2)
  
  # Resize to match
  max_dimension = max(img1.width, img1.height, img2.width, img2.height)
  img1 = resize(img1, max_dimension)
  img2 = resize(img2, max_dimension)
  
  # Add Date
  scaled_font_size = font_size*max(img1.height, img2.height)/900
  img1 = add_date(img1, scaled_font_size)
  img2 = add_date(img2, scaled_font_size)

  # Rotate to portrait before combining
  img1 = rotate(img1, landscape=False)
  img2 = rotate(img2, landscape=False)

  # Create new blank image to hold images
  combined_image = Image.new("RGB", (img1.width + img2.width, max(img1.height, img2.height)))

  # Combine the images verically
  combined_image.paste(img1, (0, 0))
  combined_image.paste(img2, (img1.width, 0))

  # Save the combined image
  combined_image.save('output/output{}.jpg'.format(i))
  