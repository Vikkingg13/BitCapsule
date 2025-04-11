# BitCapsule

BitCapsule is a modern desktop application that allows you to create time-locked Bitcoin addresses. It enables you to securely store Bitcoin funds that can only be accessed after a specific date in the future.

[⬇️ Download BitCapsule v1.0 (.exe)](https://github.com/Vikkingg13/BitCapsule/releases/download/1.0/BitCapsule.exe)

## Features
- 🔒 Create time-locked Bitcoin addresses using P2SH scripts
- 📅 User-friendly calendar interface for selecting unlock dates
- ⚡ Real-time Bitcoin block height synchronization
- 🕒 Dynamic time-until-unlock countdown
- 🎨 Modern dark-themed interface
- 📦 Export all necessary data in a convenient ZIP archive

## How it works
BitCapsule generates a special Bitcoin address using a time-lock script (CHECKLOCKTIMEVERIFY). The funds sent to this address cannot be spent until the specified block height is reached on the Bitcoin network. The application automatically calculates the target block height based on your chosen unlock date.

## Output
Each generated time capsule includes:
- QR code of the P2SH address (for receiving funds)
- QR code of the private key (for future access)
- Text file with detailed information
- Unlock date and target block information

## Security
- Private keys are generated locally
- No data is stored or transmitted online
- Open-source code for transparency
- Uses standard Bitcoin protocol features

## Requirements
- Python 3.8+
- PyQt6
- Required Python packages listed in requirements.txt

## Usage
1. Select your desired unlock date using the calendar
2. Click "Generate Time Capsule"
3. Save the generated ZIP file securely
4. Send Bitcoin to the provided P2SH address
5. Wait until the unlock date to access your funds

## Warning
⚠️ Keep your private key secure and never share it with anyone. Lost private keys cannot be recovered.

## License
MIT License

## Contributing
Contributions are welcome! Feel free to submit issues and pull requests.
