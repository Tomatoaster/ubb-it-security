import struct


class CIFF:
    """
    Holds data of a CIFF image
    """

    def __init__(
            self,
            magic_chars="CIFF",
            header_size_long=0,
            content_size_long=0,
            width_long=0,
            height_long=0,
            caption_string="",
            tags_list=None,
            pixels_list=None
    ):
        """
        Constructor for CIFF images

        :param magic_chars: the magic "CIFF" characters
        :param header_size_long: size of the header in bytes (8-byte-long int)
        :param content_size_long: size of content in bytes 8-byte-long int)
        :param width_long: width of the image (8-byte-long int)
        :param height_long: height of the image (8-byte-long int)
        :param caption_string: caption of the image (string)
        :param tags_list: list of tags in the image
        :param pixels_list: list of pixels to display
        """
        self._magic = magic_chars
        self._header_size = header_size_long
        self._content_size = content_size_long
        self._width = width_long
        self._height = height_long
        self._caption = caption_string
        if tags_list is None:
            self._tags = []
        else:
            self._tags = tags_list
        if pixels_list is None:
            self._pixels = []
        else:
            self._pixels = pixels_list
        self._is_valid = True
        self._error_message = ""

    #
    # Properties
    #

    @property
    def is_valid(self):
        """
        A flag indicating whether the the CIFF image conforms
        with the specification or not

        :return: boolean
        """
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value):
        self._is_valid = value

    @property
    def error_message(self):
        """
        An error message in case the image is not valid

        :return: str
        """
        return self._error_message
    
    @error_message.setter
    def error_message(self, value):
        self._error_message = value

    @property
    def magic(self):
        """
        The parsed magic characters

        :return: str
        """
        return self._magic

    @magic.setter
    def magic(self, value):
        self._magic = value

    @property
    def header_size(self):
        """
        The parsed header size

        :return: int
        """
        return self._header_size

    @header_size.setter
    def header_size(self, value):
        self._header_size = value

    @property
    def content_size(self):
        """
        The parsed content size

        :return: int
        """
        return self._content_size

    @content_size.setter
    def content_size(self, value):
        self._content_size = value

    @property
    def width(self):
        """
        The parsed width of the image

        :return: int
        """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        """
        The parsed height of the image

        :return: int
        """
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def caption(self):
        """
        The parsed image caption

        :return: str
        """
        return self._caption

    @caption.setter
    def caption(self, value):
        self._caption = value

    @property
    def tags(self):
        """
        The parsed list of tags

        :return: list of strings
        """
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = value

    @property
    def pixels(self):
        """
        The parsed pixels

        :return: list
        """
        return self._pixels

    @pixels.setter
    def pixels(self, value):
        self._pixels = value

    #
    # Static methods
    #

    @staticmethod
    def parse_ciff_file(file_path):
        """
        Parses a CIFF file and constructs the corresponding object

        TODO: make sure that malformed input cannot crash the parsing method

        :param file_path: path the to file to be parsed (string)
        :return: the parsed CIFF object
        """
        new_ciff = CIFF()
        bytes_read = 0
        # the following code can throw Exceptions at multiple lines
        try:
            with open(file_path, "rb") as ciff_file:
                # read the magic bytes
                magic = ciff_file.read(4)
                # read may not return the requested number of bytes
                if len(magic) != 4:
                    raise Exception("Couldn't read 4 magic bytes")
                bytes_read += 4
                # decode the bytes as 4 characters
                new_ciff.magic = magic.decode('ascii')
                if new_ciff.magic != "CIFF":
                    new_ciff.is_valid = False
                    raise Exception("Error parsing magic bytes")

                # read the header size
                h_size = ciff_file.read(8)
                if len(h_size) != 8:
                    raise Exception("Invalid image format: header size")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                # unpack returns a list
                # HINT: check the "q" format specifier!
                # HINT: Does it fit our purposes?
                new_ciff.header_size = struct.unpack("Q", h_size)[0]
                # the header size must be in [38, 2^64 - 1]
                if new_ciff.header_size < 38:
                    raise Exception("Invalid image format: header size")
                

                # read the content size
                c_size = ciff_file.read(8)
                if len(c_size) != 8:
                    raise Exception("Invalid image format: content size")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                # HINT: check out the "q" format specifier!
                # HINT: Does it fit our purposes?
                new_ciff.content_size = struct.unpack("Q", c_size)[0]

                # read the width
                width = ciff_file.read(8)
                if len(width) != 8:
                    raise Exception("Invalid image format: width")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                # HINT: check out the "q" format specifier!
                # HINT: Does it fit our purposes?
                new_ciff.width = struct.unpack("Q", width)[0]
                # the width must be in [0, 2^64 - 1]

                # read the height
                height = ciff_file.read(8)
                if len(height) != 8:
                    raise Exception("Invalid image format: height")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                # HINT: check out the "q" format specifier!
                # HINT: Does it fit our purposes?
                new_ciff.height = struct.unpack("Q", height)[0]
                # the height must be in [0, 2^64 - 1]
                if new_ciff.content_size != new_ciff.width * new_ciff.height * 3:
                    raise Exception("Invalid image format: content size not equal to width*height*3")

                # read the name of the image character by character
                caption = ""
                c = ciff_file.read(1)
                if len(c) != 1:
                    raise Exception("Invalid image format: caption format")
                bytes_read += 1
                char = c.decode('ascii')
                # read until the first '\n' (caption cannot contain '\n')
                while char != '\n':
                    # append read character to caption
                    caption += char
                    # read next character
                    c = ciff_file.read(1)
                    if len(c) != 1:
                        raise Exception("Invalid image: caption")
                    bytes_read += 1
                    char = c.decode('ascii')
                new_ciff.caption = caption

                # read all the tags
                tags = list()
                # read until the end of the header
                tag = ""
                while bytes_read != new_ciff.header_size:
                    c = ciff_file.read(1)
                    if len(c) != 1:
                        raise Exception("Invalid image: tags")
                    bytes_read += 1
                    char = c.decode('ascii')
                    if char == '\n':
                        raise Exception("Invalid image: tags")
                    # tags are separated by terminating nulls
                    tag += char
                    if char == '\0':
                        tags.append(tag)
                        tag = ""
                    # the very last character in the header must be a '\0'
                    if bytes_read == new_ciff.header_size and char != '\0':
                        raise Exception("Invalid image: tags")

                
                # all tags must end with '\0'
                for tag in tags:
                    if tag[-1] != '\0':
                        raise Exception("Invalid image: tags")
                new_ciff.tags = tags
                
                # read the pixels
                while bytes_read < new_ciff.header_size+new_ciff.content_size:
                    c = ciff_file.read(3)
                    if len(c) != 3:
                        raise Exception("Invalid image: content")
                    bytes_read += 3
                    pixel = struct.unpack("BBB", c)
                    new_ciff.pixels.append(pixel)

                # we should have reached the end of the file
                of_byte = ciff_file.read(1)
                if len(of_byte) != 0:
                    raise Exception("Invalid image: content")

        except Exception as e:
            new_ciff.is_valid = False
            new_ciff.error_message = str(e)

        return new_ciff
