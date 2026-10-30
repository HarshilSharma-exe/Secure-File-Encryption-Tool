# AES-GCM File Encryptor

A simple Python program that **locks (encrypts) and unlocks (decrypts) any file** with a password, using **AES-GCM** from Python's `cryptography` library.

If someone changes the locked file, or you type the wrong password, AES-GCM notices while decrypting. The program then refuses to unlock the file and creates **no output file**.

## Project structure

```
aes-gcm-file-encryptor/
├── encryptor.py     the main program (encrypt + decrypt + tamper check)
├── README.md        this file
├── input/           PUT the files you want to encrypt here
│   ├── notes.txt        (test file: text)
│   └── report.pdf       (test file: PDF)
├── ciphertext/      encrypted files (.enc) are saved here
└── output/          decrypted files are saved here
```

The program creates `ciphertext/` and `output/` by itself if they are missing.

## Setup (3 steps)

1. Install Python 3.8 or newer.
2. Open a terminal in this folder.
3. Install the library:

```
pip install cryptography
```

## How to use

You only type the **file name**. The program picks the right folder.

**Encrypt a file** (reads from `input/`, saves to `ciphertext/`)

```
python encryptor.py encrypt notes.txt
```

Type a password (twice). You get `ciphertext/notes.txt.enc`.

**Decrypt a file** (reads from `ciphertext/`, saves to `output/`)

```
python encryptor.py decrypt notes.txt.enc
```

Type the same password. You get `output/notes.txt`.

**To use your own file:** copy it into the `input/` folder, then encrypt it by name.

> On Windows, if `python` does not work, use `py` instead.

## Show the tamper test by hand

The program has no "tamper" command. You damage the file yourself, like a real attacker would, and AES-GCM catches it by itself when you decrypt.

Use the same password each time (for example `hello12345`).

**1. Encrypt**

```
python encryptor.py encrypt notes.txt
```

**2. Decrypt it - this works**

```
python encryptor.py decrypt notes.txt.enc
```

You get `output/notes.txt` with the original text.

**3. Make a copy and damage the copy**

- Go to the `ciphertext/` folder and copy `notes.txt.enc`. Rename the copy to `tampered_notes.txt.enc`.
- Open the copy in any editor (Notepad, VS Code, or a hex editor).
- Change **one** character (or one byte in a hex editor), or just type one extra character at the end.
- Save the file. Make sure you really changed something.

**4. Decrypt the damaged copy - it is rejected**

```
python encryptor.py decrypt tampered_notes.txt.enc
```

```
Error: Wrong password, or the file has been changed. Nothing was decrypted.
```

Now look inside the `output/` folder (`ls output` on Mac/Linux, `dir output` on Windows). There is **no** `tampered_notes.txt`. No plaintext was produced.

**5. Wrong password - also rejected**

```
python encryptor.py decrypt notes.txt.enc
```

Type a different password. You get the same error, and no new file in `output/`.

**To reset** before showing it again, delete the files inside `ciphertext/` and `output/` (keep the folders).

## How the code works

`encryptor.py` is split into small functions. Read them from top to bottom:

| Function | What it does |
|----------|--------------|
| `read_file()` / `save_file()` | Reads a file (error if missing or empty) and saves a file |
| `make_key()` | Turns your password into a 32-byte key (PBKDF2) |
| `encrypt_bytes()` | Makes a random salt and nonce, then encrypts with AES-GCM |
| `decrypt_and_verify()` | **The tamper check.** Decrypts only if the file is untouched and the password is right |
| `encrypt_file()` / `decrypt_file()` | Use the functions above on a whole file |
| `main()` | Reads the command you typed and picks the folders |

**Encrypting:** password + random salt → key → AES-GCM encrypts the file → save `salt + nonce + encrypted data`.

**Decrypting:** read the salt and nonce from the file → password + salt → same key → AES-GCM checks the tag → if OK, save the original file.

## How it meets the requirements

| Requirement | How |
|-------------|-----|
| Uses AES-GCM from a trusted library | `AESGCM` from `cryptography` |
| Key is never hard-coded or saved | Made from your password each time (`make_key`) |
| Password → key with a KDF | PBKDF2-HMAC-SHA256, 600,000 rounds, random salt |
| Unique nonce every time | `os.urandom(12)` for every encryption, saved in the file |
| Tamper detection | AES-GCM checks the tag inside `decrypt_and_verify` |
| No output if it fails | The output file is only written after the check passes |
| Errors handled | Missing file, empty file, wrong password, empty password, not-an-encrypted-file |
| Input, ciphertext and output kept apart | Three separate folders: `input/`, `ciphertext/`, `output/` |

## Why authenticated encryption?

Normal encryption only **hides** data. It does **not** tell you if someone **changed** it. An attacker could flip bits in the locked file, and you would get damaged data back without knowing.

AES-GCM adds a **tag** (a seal) to the file. When decrypting, the tag is checked first:

- Seal unbroken → you get your exact original file.
- Even **one bit** changed, or wrong password → error, you get **nothing**.

So you never receive silently corrupted or fake data.

## Good to know

- If you forget the password, the file **cannot** be recovered.
- AES-GCM cannot tell "wrong password" from "file changed", so the error message says both.
- The whole file is loaded into memory, so use normal-sized files.
- Git does not save empty folders, so on GitHub `ciphertext/` and `output/` may not appear. The program creates them automatically when needed.
