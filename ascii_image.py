import aiohttp
from dataclasses import dataclass

@dataclass
class AsciiMipmaps:
    large: str
    medium: str
    small: str

async def generate_large_ascii_image(session: aiohttp.ClientSession, prompt: str) -> str | None:
    try:
        url = "https://bejamas.com/api/create-ascii.data"
        payload = {"prompt": prompt, "backgroundColor": "#000000", "foregroundColor": "#ffffff", "id": "64d5d8126c3d"}

        # Send a POST request with form-encoded data
        response = await session.post(url, data=payload)
        list = await response.json(content_type=None)

        next_is_image = False

        for item in list:
            if next_is_image:
                return item
            if item == "dots":
                next_is_image = True
    except:
        return None
    return None

def ascii_average_4(a: str, b: str, c: str, d: str):
    a_code = ord(a)
    b_code = ord(b)
    c_code = ord(c)
    d_code = ord(d)

    avg_code = (a_code + b_code + c_code + d_code) / 4

    closest = a
    closest_diff = abs(avg_code - a_code)

    for char, code in [(b, b_code), (c, c_code), (d, d_code)]:
        diff = abs(avg_code - code)
        if diff < closest_diff:
            closest_diff = diff
            closest = char

    return closest

def shrink_ascii_image(image: str):
    shrank = ""

    lines = list(filter(lambda line: not line.isspace() and len(line) != 0, image.splitlines()))

    for line_i in range(0, len(lines), 2):
        if line_i + 1 >= len(lines):
            break
        line = lines[line_i]
        line_p1 = lines[line_i+1]
        for char_i in range(0, len(line), 2):
            if char_i + 1 >= len(line):
                break
            char_l = line[char_i]
            char_r = line[char_i+1]
            char_p1_l = line_p1[char_i]
            char_p1_r = line_p1[char_i+1]
            shrank += ascii_average_4(char_l, char_r, char_p1_l, char_p1_r)
        
        shrank += "\n"

    return shrank

async def generate_ascii_image(session: aiohttp.ClientSession, prompt: str) -> AsciiMipmaps | None:
    image = await generate_large_ascii_image(session, prompt)
    if image is None or len(image.strip()) == 0:
        return None
    
    large = image
    medium = shrink_ascii_image(large)
    small = shrink_ascii_image(medium)

    return AsciiMipmaps(large, medium, small)

if __name__ == "__main__":
    prompt = input("Prompt: ")
    image = generate_large_ascii_image(prompt)
    if image is None or len(image.strip()) == 0:
        print("Unable to generate image.")
        exit(1)
    print("----------- FULL SIZE IMAGE -----------")
    print(image)
    print("----------- RESIZED IMAGE -----------")
    print(shrink_ascii_image(image))

WIZARD = """    :%@▓▓▒&+-:
    .--=&▒████▒%.
         .▓████▓▒+
          .█████░▓▒=
           #█████&░█*
           *█████░#@#*.
           *█████▒*@%*▒-
           ▓████████▓▓▓▓@&*:.
       .:*░████████▓▓▒▒░▓███▒░%:    .*░░░░#*:
   .=*&░████▓█▓#█▓░#@&#████████%   %▓▓&+*+&██*
   =███████▓=#@:▒@-=&=&▓████@*:   %█#.   . :░█&
    -#░░░▒░. -+ :&#.%▓=@++:       %█=.     :*█#
       +*░▓+:#-  % :.   *         %█*:    ..&█&
    :%███████▓:  :      %*:       -▒█&*░@=+@█&
 :=#██████████#         :▒█%       .#█░███░&-
&▓█████@░░█████          @██@       -▒+██&
*▓██████░#*%@██*         -██=        %██▓
  +█████████@*@█*        -██-        :▒██=
  %█████████████▒+       :▓█▒-        -██.
 =▓████▓█████████▒=.    .#▓██▒%=:::..-*#@+=
 %████████████████░@    @▒██████░-#&+++▒&&#-
-▒██████████████████#. +▓███████▒%█@#██▓*&&"""

def find_longest_line(text: str):
    longest = 0
    for line in text.splitlines():
        l = len(line)
        if l > longest:
            longest = l
    return longest

WIZARD_W = find_longest_line(WIZARD)
WIZARD_H = len(WIZARD.splitlines())
