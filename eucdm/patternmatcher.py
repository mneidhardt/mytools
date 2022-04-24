import re
import string
import random

class PatternMatcher():
    
    # Class for handling formats of the EUCDM.
    # They have several different formats:
    # Format       My interpretation, based on EU Law:
    # a2        => Alphabetic characters, exactly 2 of them.
    # a..2      => Alphabetic characters, 0 to 2 of them.
    # an2       => Alphanumeric characters, exactly 2 of them.
    # an..2     => Alphanumeric characters, 0 to 2 of them.
    # n4        => integer with 4 digits.
    # n4,2      => float with 4 digits, up to 2 of which are decimals.
    # n..4      => integer with 0 to 4 digits.
    # n..4,2    => float with 0 to 4 digits, up to 2 of which are decimals.
    #--------------------------------------------------------------------

    def __init__(self):
        self.patterns = []
        self.patterns.append(re.compile('^a(\d+)$', re.IGNORECASE))
        self.patterns.append(re.compile('^a\.\.(\d+)$', re.IGNORECASE))
        self.patterns.append(re.compile('^an(\d+)$', re.IGNORECASE))
        self.patterns.append(re.compile('^an\.\.(\d+)$', re.IGNORECASE))
        self.patterns.append(re.compile('^n(\d+)$'))
        self.patterns.append(re.compile('^n(\d+),(\d+)$'))
        self.patterns.append(re.compile('^n\.\.(\d+)$'))
        self.patterns.append(re.compile('^n\.\.(\d+),(\d+)$'))
        self.patterns.append(re.compile('^\s*$'))

    # Test version of 'n..N,M' that allows empty string, using regex.
    def altVersion(self, format):
        p = re.compile('^(\d{1,6}|\d{1,4},\d{1,2})?$')
        if p.match(format):
            return True
        else:
            return False

    # Test version of '..N' that allows empty string, using regex.
    def altVersion2(self, format):
        p = re.compile('^\d{0,6}$')
        if p.match(format):
            return True
        else:
            return False

    # Converts EUCDM format to restrictions used in JSON Schema.
    def getRestrictions(self, format):
        match = self.patterns[0].match(format)
        if match:
            minmax = '{' + match.group(1) + '}'
            return [['type', 'string'], ['pattern', '^[a-åA-Å]'+minmax+'$']]

        match = self.patterns[1].match(format)
        if match:
            minmax = '{0,' + match.group(1) + '}'
            return [['type', 'string'], ['pattern', '^[a-åA-Å]'+minmax+'$']]

        match = self.patterns[2].match(format)
        if match:
            minmax = '{' + match.group(1) + '}'
            return [['type', 'string'], ['pattern', '^[a-åA-Å0-9]'+minmax+'$']]

        match = self.patterns[3].match(format)
        if match:
            minmax = '{0,' + match.group(1) + '}'
            return [['type', 'string'], ['pattern', '^[a-åA-Å0-9]'+minmax+'$']]

        match = self.patterns[4].match(format)  # e.g. "n6".
        if match:
            size = int(match.group(1))
            min = pow(10, size-1)
            max = pow(10, size)-1
            return [['type', 'integer'], ['minimum', min], ['maximum', max]]

        match = self.patterns[5].match(format)  # e.g. "n6,2".
        if match:
            size1 = int(match.group(1)) # Size of the whole expression.
            size2 = int(match.group(2)) # Size of the decimals part.
            decimals = pow(10, -1*size2)
            min = pow(10, size1-size2-1)
            max = pow(10, size1)-1
            return [['type', 'number'], ['minimum', min], ['maximum', max], ['multipleOf', decimals]]

        match = self.patterns[6].match(format)  # e.g. "n..8".
        if match:
            size = int(match.group(1)) # Size of the whole expression.
            min = 0
            max = pow(10, size)-1
            return [['type', 'integer'], ['minimum', min], ['maximum', max]]

        match = self.patterns[7].match(format)  # e.g. "n..12.2".
        if match:
            size1 = int(match.group(1)) # Size of the whole expression.
            size2 = int(match.group(2)) # Size of the decimals part.
            decimals = pow(10, -1*size2)
            min = 0.0
            max = pow(10, size1)-1
            return [['type', 'number'], ['minimum', min], ['maximum', max], ['multipleOf', decimals]]

        match = self.patterns[8].match(format)
        if match:
            return []

        raise ValueError('Format "' + format + '" not understood.')

    def generateSample(self, format):
        match = self.patterns[0].match(format)
        if match:
            size = int(match.group(1))
            return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=size))
         
        match = self.patterns[1].match(format)
        if match:
            size = int(match.group(1))
            return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=size))

        match = self.patterns[2].match(format)
        if match:
            size = int(match.group(1))
            return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=size))

        match = self.patterns[3].match(format)
        if match:
            size = int(match.group(1))
            return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=size))

        # In principle, the 'nX,Y' and 'n..X,Y' patterns allow for results where you can omit the separator
        # and use all fields for digits, producing an integer of X digits. I dont handle that in this generator,
        # as it's only meant to produce dummy data for test instances.
        #--------------------------------------------------------------------
        mydigits = '123456789'      # I dont want leading zeros.
        match = self.patterns[4].match(format)
        if match:
            size = int(match.group(1))
            return int(''.join(random.choices(mydigits, k=size)))

        match = self.patterns[5].match(format)
        if match:
            size1 = int(match.group(1))
            size2 = int(match.group(2))
            return float(''.join(random.choices(mydigits, k=size1-size2)) + '.' + ''.join(random.choices(mydigits, k=size2)))

        match = self.patterns[6].match(format)
        if match:
            size = int(match.group(1))
            return int(''.join(random.choices(mydigits, k=size)))

        match = self.patterns[7].match(format)
        if match:
            size2 = int(match.group(2))
            size1 = int(match.group(1))
            return float(''.join(random.choices(mydigits, k=size1-size2)) + '.' + ''.join(random.choices(mydigits, k=size2)))

        match = self.patterns[8].match(format)
        if match:
            return ''
