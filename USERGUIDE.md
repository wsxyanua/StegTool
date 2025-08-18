# STEGANOGRAPHY v1.0 - USER GUIDE

## OVERVIEW

Steganography v1.0 is a tool for hiding secret messages inside images because apparently regular encryption wasn't sneaky enough. Available as both web application and desktop software for maximum convenience and paranoia levels.

## WEB APPLICATION

### GETTING STARTED

1. Open `web/index.html` in your browser
2. Choose between HIDE or EXTRACT tabs
3. Select steganography method: LSB for beginners, DCT/DWT for show-offs

### HIDING MESSAGES

1. **Select File**: Click to select PNG/BMP/TIFF image
2. **Enter Message**: Type your secret message in the text area
3. **Set Password**: Optional encryption password for security
4. **Choose Method**: 
   - LSB: Standard method, good capacity
   - DCT: Frequency domain, more robust
   - DWT: Wavelet domain, advanced hiding
5. **Generate Signature**: Optional digital signature for authenticity
6. **Hide Message**: Click to process and download result

### EXTRACTING MESSAGES

1. **Select File**: Choose image containing hidden message
2. **Enter Password**: If message was encrypted
3. **Choose Method**: Must match the hiding method used
4. **Extract Message**: Click to reveal hidden content
5. **Verify Signature**: Optional signature verification

### AUDIO STEGANOGRAPHY

1. **Supported Formats**: MP3, WAV, FLAC
2. **Methods Available**:
   - LSB: Hide in audio sample bits
   - Phase: Modify frequency phase
   - Echo: Use echo delays for encoding
3. **Process**: Same as image steganography

### SETTINGS MANAGEMENT

- **Export Settings**: Save encrypted configuration backup
- **Import Settings**: Restore from backup file
- **Theme Toggle**: Switch between light/dark modes

## DESKTOP APPLICATION

### INSTALLATION

1. Download `main.py` and required dependencies
2. Install Python 3.7+ with PIL and numpy
3. Run: `python main.py`

### FEATURES

- **Recent Files**: Quick access to previously used images
- **Settings Export/Import**: Backup your preferences
- **Portable Mode**: Settings saved in application folder
- **Professional Interface**: Clean, modern design

### HIDING PROCESS

1. **File Menu**: Open image or select from recent files
2. **Hide Tab**: Enter message and optional password
3. **Capacity Display**: Shows maximum message length
4. **Character Counter**: Real-time message length tracking
5. **Save Result**: Choose output location for stego image

### EXTRACTION PROCESS

1. **Extract Tab**: Select image with hidden message
2. **Password**: Enter if message was encrypted
3. **View Result**: Extracted message appears in text area

## SUPPORTED FORMATS

### IMAGES
- **PNG**: Recommended for best quality
- **BMP**: Uncompressed, reliable
- **TIFF**: Professional format support
- **JPEG**: Converted to PNG automatically

### AUDIO
- **WAV**: Uncompressed, best quality
- **MP3**: Compressed format support
- **FLAC**: Lossless compression

## SECURITY FEATURES

### ENCRYPTION
- **AES-256**: Military-grade encryption
- **PBKDF2**: Key derivation function
- **Salt**: Random salt for each encryption

### DIGITAL SIGNATURES
- **RSA**: Public key cryptography
- **Key Generation**: Automatic keypair creation
- **Verification**: Authenticity checking

### PRIVACY
- **Client-Side**: All processing in browser
- **No Upload**: Files never leave your device
- **Portable**: Desktop app stores settings locally

## BEST PRACTICES

### MESSAGE HIDING
1. Use PNG format for best results
2. Choose strong passwords (12+ characters)
3. Keep messages under 80% of capacity
4. Use DCT/DWT for important messages

### SECURITY
1. Always use encryption for sensitive data
2. Generate digital signatures for authenticity
3. Verify extracted messages carefully
4. Store backup of original images

### FILE MANAGEMENT
1. Keep original images separate
2. Use descriptive filenames
3. Export settings regularly
4. Clear recent files when needed

## TROUBLESHOOTING

### COMMON ISSUES

**Message Too Long**
- Check capacity display
- Reduce message length
- Use larger image

**Extraction Failed**
- Verify correct password (did you forget it already?)
- Check steganography method
- Ensure image wasn't modified

**File Not Supported**
- Convert JPEG to PNG
- Use uncompressed formats
- Check file corruption

**Browser Issues**
- Use modern browser
- Enable JavaScript
- Check file size limits

### ERROR MESSAGES

**"No hidden message found"**
- Wrong extraction method
- Image doesn't contain message
- File was modified after hiding

**"Password required"**
- Message was encrypted
- Enter correct password
- Check password case sensitivity

**"Invalid file format"**
- Use supported formats only
- Check file extension
- Verify file integrity

## TECHNICAL DETAILS

### ALGORITHMS
- **LSB**: Least Significant Bit replacement
- **DCT**: Discrete Cosine Transform domain
- **DWT**: Discrete Wavelet Transform domain

### CAPACITY CALCULATION
- LSB: Width × Height × Channels ÷ 8 characters
- DCT: Approximately 60% of LSB capacity
- DWT: Approximately 40% of LSB capacity

### PERFORMANCE
- **Web**: Client-side processing, no server needed
- **Desktop**: Native performance, larger file support
- **Memory**: Efficient algorithms, minimal RAM usage

## SUPPORT

For issues or questions:
1. Check this user guide
2. Review error messages carefully
3. Verify file formats and sizes
4. Test with simple messages first

## VERSION HISTORY

**v1.0** - Initial release
- LSB, DCT, DWT steganography
- Audio steganography support
- Web and desktop applications
- Professional UI design
- Settings management
- Digital signatures
