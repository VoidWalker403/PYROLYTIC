# Linux and Windows Development: From First Principles to Independent Projects

**A practical handbook, curriculum, reference, and project workbook**  
Prepared: 15 September 2026  
Starting level: no programming or command-line experience required.

## Start here

Your destination is the ability to start with a problem and an empty folder, design a solution, write it, investigate failures, test it, deliver it, and maintain it on Linux and Windows.

“Development” has several meanings. This handbook covers **developing software on both operating systems**, **building software specifically for each platform**, and the foundations for **systems, infrastructure, and operating-system development**. It also maps adjacent fields so you can choose a specialization deliberately.

No single document can teach every API, language, hardware device, and engineering discipline in full. This is a substantial foundation and a connected route into those subjects. The early chapters explain and demonstrate core skills; advanced chapters identify prerequisites, mechanisms, exercises, and specialist references. You can build useful projects long before finishing the advanced material.

**Suggested route:** chapters 1–12 → project A → chapters 13–20 → projects B and C → chapters 21–26 → project D → one specialization from chapter 27. Return to deeper systems material as your projects need it.

**Practice environment:** use a new learning folder with invented data. Commands marked **Bash** run inside Linux; commands marked **PowerShell** run in Windows PowerShell or PowerShell as specified. Do not paste one shell's commands into the other. Installation commands below are instructions for your future practice; writing this handbook has not installed software or changed your operating system.

**Evidence:** explanations and exercises are original teaching material. Official documentation, university courses, and author/publisher resources were consulted while preparing this guide; the CMake site could not be retrieved during verification. Software support and installation requirements change; consult the linked installation pages when setting up. The validation appendix distinguishes checked examples from examples that still need testing on your machines.

## Contents

1. [What mastery means](#1-what-mastery-means)
2. [Prerequisites and computer foundations](#2-prerequisites-and-computer-foundations)
3. [Set up a two-platform laboratory](#3-set-up-a-two-platform-laboratory)
4. [Files, paths, text, and permissions](#4-files-paths-text-and-permissions)
5. [Linux terminal and Bash](#5-linux-terminal-and-bash)
6. [Windows terminal and PowerShell](#6-windows-terminal-and-powershell)
7. [Programming foundations with Python](#7-programming-foundations-with-python)
8. [A complete first command-line program](#8-a-complete-first-command-line-program)
9. [Git and engineering workflow](#9-git-and-engineering-workflow)
10. [Algorithms, data structures, and mathematics](#10-algorithms-data-structures-and-mathematics)
11. [C, memory, compilation, and linking](#11-c-memory-compilation-and-linking)
12. [C++, Rust, C#, and choosing languages](#12-c-rust-c-and-choosing-languages)
13. [Operating-system internals](#13-operating-system-internals)
14. [Linux systems development](#14-linux-systems-development)
15. [Windows systems development](#15-windows-systems-development)
16. [Networking and protocols](#16-networking-and-protocols)
17. [SQL, databases, and persistent data](#17-sql-databases-and-persistent-data)
18. [Web applications and APIs](#18-web-applications-and-apis)
19. [Desktop applications and user interfaces](#19-desktop-applications-and-user-interfaces)
20. [Testing, debugging, and performance](#20-testing-debugging-and-performance)
21. [Security engineering](#21-security-engineering)
22. [Build systems, packaging, and releases](#22-build-systems-packaging-and-releases)
23. [Containers, virtual machines, and cloud](#23-containers-virtual-machines-and-cloud)
24. [Operations, reliability, and recovery](#24-operations-reliability-and-recovery)
25. [Architecture and designing from scratch](#25-architecture-and-designing-from-scratch)
26. [Cross-platform engineering](#26-cross-platform-engineering)
27. [Adjacent domains and specialization routes](#27-adjacent-domains-and-specialization-routes)
28. [Projects with acceptance criteria](#28-projects-with-acceptance-criteria)
29. [Study schedule and mastery checkpoints](#29-study-schedule-and-mastery-checkpoints)
30. [Books, courses, and documentation](#30-books-courses-and-documentation)
31. [Troubleshooting playbook](#31-troubleshooting-playbook)
32. [Glossary and independent-build checklist](#32-glossary-and-independent-build-checklist)
33. [Validation and limitations](#33-validation-and-limitations)

---

## 1. What mastery means

Mastery is observable ability, not a count of tutorials completed. You should eventually be able to:

- Explain how your program moves from source code to a running process.
- Use both command lines without relying on copied commands you cannot explain.
- Choose data structures, storage, and interfaces that fit the problem.
- Read documentation and implement a feature you have never built before.
- Diagnose a crash, failed request, permission problem, and slow operation.
- Handle invalid input and partial failure without corrupting user data.
- Build and test on both platforms using repeatable instructions.
- Package a release and verify it on a clean machine or virtual machine.
- Explain your security boundaries and restore a backup.
- Maintain a project after the initial demonstration works.

There are four useful levels:

1. **Foundation:** small scripts, files, functions, shell use, and Git.
2. **Independent builder:** complete CLI, desktop, or web projects with tests and documentation.
3. **Professional engineer:** reliable releases, operational judgment, architecture, performance, and teamwork.
4. **Specialist:** deep expertise in a field such as kernels, compilers, graphics, distributed systems, or security.

Aim for level 2 first. Build level 3 through repeated releases. Pick one level-4 field rather than trying to become an expert in every field simultaneously.

### The learning loop

For each topic: read a short explanation → predict an example's behavior → run it → change it → break it deliberately → diagnose it → rebuild without the tutorial → explain it in your own words.

Keep a learning journal with four entries: what I expected, what happened, what caused the difference, and what experiment would confirm that explanation. An error you investigated teaches more than ten commands you copied successfully.

## 2. Prerequisites and computer foundations

### 2.1 Basic working skills

Learn to create and locate folders, show filename extensions, edit plain text, install software from its official source, inspect free disk space, and extract archives. Know the difference between saving a file and running a program.

Use a code editor with syntax highlighting, search, a terminal, and a debugger. Learn find-in-files, jump-to-definition, rename-symbol, format-document, and breakpoints. These are more valuable initially than extensive theme or plugin customization.

### 2.2 What the hardware does

- **CPU:** executes instructions. A core can run an instruction stream; multiple cores allow work to overlap in hardware.
- **RAM:** holds active code and data. Its contents generally disappear when power is lost.
- **Storage:** retains files. Reading an SSD is still much slower than accessing nearby CPU caches.
- **Cache:** stores frequently used data closer to the processor. Data layout can matter as much as instruction count.
- **GPU:** performs large amounts of parallel work, useful for graphics and some numerical workloads.
- **Network interface:** sends and receives data through a local or wider network.
- **Firmware and bootloader:** initialize hardware and arrange for the operating-system kernel to start.

Example: a photo editor reads compressed image bytes from storage, decodes them into RAM, changes pixel data using CPU/GPU work, and writes a new file. A progress bar that stops moving could indicate a busy CPU, a blocked disk request, or a frozen UI thread. These need different fixes.

### 2.3 Software layers

Think of a program as moving through layers:

```text
User action
  -> application logic
  -> language runtime and libraries
  -> operating-system services
  -> device drivers
  -> hardware
```

The **kernel** manages privileged access to hardware and resources. A **shell** starts commands. A **terminal** displays and transports interactive input/output. A **compiler** translates source into another representation. A **runtime** supplies execution services such as garbage collection or module loading.

Windows Terminal is not PowerShell. Bash is not Linux. An editor is not necessarily a compiler. Keeping these distinctions clear makes troubleshooting easier.

### 2.4 Numbers and text

Learn binary, hexadecimal, signed integers, floating-point numbers, bytes, Unicode, and UTF-8.

- Eight bits form a byte. Hexadecimal writes four bits per digit: decimal 255 is hexadecimal `FF`.
- `1 KiB` means 1,024 bytes; `1 kB` means 1,000 bytes. Tools sometimes label these inconsistently.
- A 32-bit unsigned integer holds values from 0 to 4,294,967,295.
- Floating-point arithmetic approximates many fractions; do not expect every decimal calculation to be exact.
- A character is not necessarily one byte, one Unicode code point, or one visible glyph.

**Exercise:** save a file containing `hello`, a Hindi word, and an emoji in UTF-8. Compare its character count and byte size. Explain why they differ.

### 2.5 Mathematics you actually need

Begin with arithmetic, fractions, percentages, algebra, Boolean logic, sets, and functions. Add graphs, probability, and basic statistics for algorithms and data work. Linear algebra matters for graphics and machine learning; calculus matters for optimization and simulation. You do not need advanced calculus before writing your first useful application.

**Checkpoint:** explain CPU versus RAM versus disk; source file versus executable; terminal versus shell; absolute versus relative path; and binary data versus text.

## 3. Set up a two-platform laboratory

### 3.1 A sensible starting arrangement

If your main computer runs Windows, use native Windows tools plus a Linux distribution in WSL 2. Add a separate Linux virtual machine later for boot, storage, networking, and service-administration exercises. WSL is convenient for Linux programming, but it is not a substitute for every bare-metal or VM experiment.

A modest computer is enough for scripts and small projects. As a planning guideline, 16 GB RAM gives more room for an editor, browser, and VM; 8 GB can work with fewer simultaneous tools. These are learning-lab suggestions, not vendor minimum requirements. Start with existing hardware and measure constraints before buying upgrades.

### 3.2 Windows setup

Install tools from their official distribution channels:

1. A code editor and Git.
2. Python 3.
3. PowerShell 7 when you reach substantial scripting; distinguish it from Windows PowerShell 5.1.
4. WSL and a beginner-friendly distribution such as Ubuntu.
5. Later: a supported .NET SDK for C#, and Visual Studio C++ build tools plus the Windows SDK for native C/C++.

PowerShell, **administrator session for installation only**:

```powershell
wsl --install
```

Restart if requested and finish the Linux user setup. Then inspect your installation in an ordinary PowerShell session:

```powershell
wsl --list --verbose
$PSVersionTable.PSVersion
git --version
py --version
```

The `py` command depends on how Python was installed. If unavailable, locate your Python installation and use its documented command. Do not assume that `python`, `py`, and your editor all select the same interpreter.

Use Microsoft's [WSL installation instructions](https://learn.microsoft.com/en-us/windows/wsl/install) for current prerequisites and its [environment setup guide](https://learn.microsoft.com/en-us/windows/wsl/setup/environment) for integration details.

### 3.3 Linux setup

Inside an Ubuntu or Debian practice environment, **Bash**:

```bash
sudo apt update
sudo apt install build-essential git python3 python3-venv gdb strace cmake
mkdir -p "$HOME/dev-lab"
cd "$HOME/dev-lab"
uname -a
python3 --version
gcc --version
```

`apt update` refreshes available-package information; `apt install` installs the named packages and dependencies. These commands are distribution-specific. Fedora and other distributions use different package managers and package names.

`sudo` runs a command with elevated privileges when your account is authorized. It is appropriate for system package installation, not a default prefix for development commands.

### 3.4 Keep environments separate

Keep Linux-heavy WSL projects in the Linux filesystem, such as `~/dev-lab`, and native Windows projects in a Windows folder such as `C:\Users\yourname\dev-lab`. The same source can be exchanged through Git, but executable files and virtual environments belong to their platform.

Record tool versions in each project's README. A Python virtual environment created on Windows cannot simply become a Linux environment by copying the folder.

### 3.5 First environment exercise

Create `hello.py` containing `print("Hello from my development lab")`. Run it once with Windows Python and once with Linux Python. Record the commands, interpreter paths, working directories, and output. The visible output can match even though different executables and operating systems performed the work.

**Checkpoint:** independently launch both shells, locate a project, run a program, and explain which OS and interpreter ran it.

## 4. Files, paths, text, and permissions

### 4.1 Filesystem vocabulary

A filesystem associates names with stored data and metadata. A directory organizes names; a path tells the OS how to locate one.

- An **absolute path** starts from a filesystem root: `/home/learner/code` or `C:\Users\learner\code`.
- A **relative path** is interpreted from a current directory: `data/input.txt`.
- `.` denotes the current directory; `..` its parent.
- An **extension** is a naming convention, not proof of the file's content.
- A **symbolic link** refers to another path; a **hard link** is another directory entry for the same underlying file on a supported filesystem.

Linux commonly uses `/home` for user homes, `/etc` for system configuration, `/var` for changing system data, `/tmp` for temporary files, and `/usr` for much installed user-space software. Windows commonly uses user-profile directories, `Program Files`, and application-data locations. Learn the appropriate platform location instead of putting every file beside an executable.

### 4.2 Case, separators, and newlines

Linux filesystems are commonly case-sensitive; typical Windows directories are case-insensitive, though configuration and filesystem choices can change this. A program importing `Parser.py` as `parser` may work in one environment and fail in another.

Use path libraries rather than assembling paths with string concatenation. Avoid filenames differing only by case. Save source as UTF-8. Agree on newline rules in the repository rather than manually converting files repeatedly.

### 4.3 Permissions

Traditional Linux mode bits distinguish owner, group, and others, with read/write/execute permissions. For a directory, execute generally means traversal; write concerns directory entries; read concerns listing names. Changing a file's permissions is not the same as changing its parent directory's permissions.

Example in a Linux practice folder:

```bash
printf '%s\n' 'private practice note' > note.txt
chmod 600 note.txt
ls -l note.txt
```

`600` grants read/write to the owner and no mode-bit permissions to group or others. Additional controls, filesystem features, and privileged users still matter. Do not solve unexplained failures by granting everyone every permission.

Windows uses security identities and access-control lists. In PowerShell:

```powershell
Get-Acl -LiteralPath . | Format-List
```

Inspect an ACL before modifying it. Learn inheritance and the identity running your process. A service and your signed-in desktop session may have different access even when running identical code.

### 4.4 Paths are part of your input contract

If an app accepts a filename, decide whether it may read anywhere or only beneath a designated directory. `../` components and symbolic links can escape naive folder checks. For a production import service, use platform-aware path validation and explicit storage boundaries.

**Exercise:** create files with spaces, mixed case, and non-ASCII names. Read them using a path library on both OSes. Repeat from a different working directory. Explain each failure.

## 5. Linux terminal and Bash

### 5.1 Essential commands, organized by purpose

- Location and files: `pwd`, `ls`, `cd`, `mkdir`, `cp`, `mv`.
- Reading: `cat`, `less`, `head`, `tail`.
- Searching: `rg` when installed, `grep`, `find`.
- Text processing: `sort`, `uniq`, `cut`, `sed`, `awk`.
- Processes: `ps`, `top`, `jobs`, `fg`, `kill`.
- Storage: `df`, `du`.
- Help: `man`, `command --help`, `type`, `command -v`.

Do not memorize every flag. Learn to answer a question such as “Which files contain this error?” or “Which executable will run?”

```bash
pwd
command -v python3
mkdir -p samples
printf '%s\n' INFO ERROR INFO > samples/events.log
grep '^ERROR' samples/events.log
sort samples/events.log | uniq -c
```

The last command groups identical lines and counts them. A pipe connects one command's standard output to the next command's standard input.

### 5.2 Streams and exit status

A conventional command has standard input, standard output, and standard error. A program should write useful data to standard output and diagnostic messages to standard error so pipelines remain usable.

```bash
python3 report.py > report.txt 2> errors.txt
printf 'Exit status: %s\n' "$?"
```

This assumes you have written `report.py`. `>` overwrites the destination; `>>` appends. `$?` contains the previous command's status, conventionally zero for success. Read it immediately, before another command replaces it.

### 5.3 Quoting and expansion

```bash
project_dir="$HOME/dev-lab/a project"
mkdir -p "$project_dir"
printf '%s\n' "$project_dir"
printf '%s\n' '$HOME is literal inside single quotes'
```

Double quotes allow variable expansion while preserving spaces in an argument. Single quotes suppress ordinary expansion. Unquoted variables may undergo word splitting and wildcard expansion. This is why a script that works for `report.txt` may break for `quarterly report.txt`.

### 5.4 Your first Bash script

Save as `count-lines.sh`, with LF newlines:

```bash
#!/usr/bin/env bash
set -eu

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s FILE\n' "$0" >&2
  exit 2
fi

if [ ! -f "$1" ] || [ ! -r "$1" ]; then
  printf 'Expected a readable regular file: %s\n' "$1" >&2
  exit 1
fi

wc -l < "$1"
```

Run `bash count-lines.sh samples/events.log`; expect `3`. `$#` is argument count, `$1` the first argument, and `$0` the invoked script name. `wc -l` counts newline characters, so a final unterminated text line needs special consideration.

`set -e` and `set -u` catch some failures and unset-variable mistakes, but shell error handling has context-dependent exceptions. Learn explicit status checking for important operations. Bash's `pipefail` option can expose failures inside pipelines; it is not portable to every shell.

### 5.5 Automation principles

Write scripts that work twice, fail clearly, quote paths, accept parameters, and do not depend on an accidental current directory. Use a preview mode for bulk modifications. Avoid parsing formatted file listings when tools provide direct file APIs.

**Checkpoint:** write a script that scans a practice log directory, reports matching lines, and handles a missing folder and filenames containing spaces.

## 6. Windows terminal and PowerShell

### 6.1 Think in objects

Bash commonly passes byte/text streams. PowerShell cmdlets commonly pass structured objects with properties and methods. Native external programs still have their own argument, output, and exit-code behavior.

```powershell
Get-Process |
    Sort-Object WorkingSet64 -Descending |
    Select-Object -First 5 ProcessName, Id, WorkingSet64
```

This sorts process objects by a numeric property, then selects fields. It does not extract columns from a screenshot-like text listing. Use `Get-Member` to discover object structure.

```powershell
Get-Process | Get-Member
Get-Help Get-ChildItem -Examples
Get-Command python -ErrorAction SilentlyContinue
```

Official reference: [PowerShell overview](https://learn.microsoft.com/en-us/powershell/scripting/overview).

### 6.2 Files and data

```powershell
$practiceDir = Join-Path $env:USERPROFILE 'dev-lab'
New-Item -ItemType Directory -Path $practiceDir -Force | Out-Null
Get-ChildItem -LiteralPath $practiceDir -File |
    Select-Object Name, Length |
    ConvertTo-Json
```

`Join-Path` builds a path. `-LiteralPath` treats wildcard characters literally. `Out-Null` discards output you do not want to show. `ConvertTo-Json` serializes selected properties as data; explicitly choose properties and serialization depth for complex objects.

### 6.3 A reusable script

Save as `Get-LargePracticeFiles.ps1`:

```powershell
param(
    [Parameter(Mandatory = $true)]
    [string]$Folder,

    [ValidateRange(0, [long]::MaxValue)]
    [long]$MinimumBytes = 1024
)

$ErrorActionPreference = 'Stop'
try {
    Get-ChildItem -LiteralPath $Folder -File |
        Where-Object Length -GE $MinimumBytes |
        Select-Object Name, Length, FullName
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
```

Run in your practice directory:

```powershell
.\Get-LargePracticeFiles.ps1 -Folder . -MinimumBytes 0
```

Parameters are the script's input interface. Validation rejects unsuitable values. `try`/`catch` handles terminating errors; `$ErrorActionPreference = 'Stop'` makes many cmdlet errors terminating. Check `$LASTEXITCODE` explicitly after native tools such as a compiler; PowerShell cmdlet error handling does not automatically cover every external-program failure.

Execution policy and organization policy may affect script launch. Inspect the policy and follow your environment's approved setup; a blocked script is not a reason to disable machine-wide controls indiscriminately.

### 6.4 Windows administration concepts

Learn services, Task Scheduler, Event Viewer, environment variables, Registry configuration, CIM, NTFS permissions, and user versus administrator contexts. Use readable cmdlet names in scripts; aliases such as `ls` can hide differences from Linux tools.

**Exercise:** export a CSV of selected running-process properties, import it again, filter by memory usage, and explain why imported CSV values may need numeric conversion.

**Checkpoint:** write a parameterized script, inspect objects, export structured data, and handle both a cmdlet error and a native program's nonzero exit code.

## 7. Programming foundations with Python

### 7.1 Learn these ideas in order

1. Values and types: integers, strings, booleans, and missing values.
2. Variables and expressions: names and calculations.
3. Branches and loops: decisions and repetition.
4. Functions: named behavior with inputs and outputs.
5. Collections: lists, dictionaries, sets, and tuples.
6. Files, encoding, and structured formats such as JSON and CSV.
7. Errors and exceptions.
8. Modules, packages, virtual environments, and dependencies.
9. Tests, debugging, and small program design.
10. Classes, iterators, type hints, and asynchronous work when needed.

### 7.2 Values, loops, and functions

```python
def summarize_sizes(sizes):
    if any(size < 0 for size in sizes):
        raise ValueError("Sizes cannot be negative")
    return {"files": len(sizes), "total_bytes": sum(sizes)}

print(summarize_sizes([100, 250, 50]))
```

Expected output: `{'files': 3, 'total_bytes': 400}`. The list is an ordered collection; the dictionary names each result. `raise` reports invalid input. This function assumes a list of comparable numeric sizes; public interfaces may need stricter type validation.

Separate pure calculations from input/output. A function that sums supplied values is easier to test than one that also reads a disk, opens a dialog, and sends an email.

### 7.3 Mutable values and identity

Two variables can refer to the same list. Changing the list through one name affects what the other name sees. Copying a reference is different from copying the entire object. Learn shallow versus deep copies, and avoid mutable default arguments in functions.

Use a class when combining state and behavior clarifies the domain; do not turn every helper function into a class. Favor simple modules until shared state and interfaces justify more structure.

### 7.4 Environments

In a new Windows practice project:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip --version
```

Equivalent Linux setup:

```bash
python3 -m venv .venv
.venv/bin/python -m pip --version
```

An environment isolates project packages, not permissions or malicious code. Invoke its interpreter explicitly to avoid activation-policy confusion. Use `python -m pip` with the intended interpreter instead of assuming an unrelated `pip` command targets it.

### 7.5 Reading documentation

For any function, identify parameters, return value, exceptions, side effects, and version requirements. Write a five-line experiment before incorporating an unfamiliar API into a large program.

The [Python tutorial](https://docs.python.org/3/tutorial/) is an excellent language reference after your first programming lessons. Absolute beginners can start with *Automate the Boring Stuff with Python* or CS50; see chapter 30.

**Checkpoint:** read a UTF-8 file, count selected values, validate input, write JSON, and test your calculation independently of filesystem access.

## 8. A complete first command-line program

Build **File Summary**, a read-only utility that lists immediate files in a folder and their byte sizes. It deliberately does not recurse or follow symbolic links. This small scope makes its behavior easy to understand.

### 8.1 The program

Save as `file_summary.py` in a fresh project:

```python
import argparse
import json
from pathlib import Path
import stat
import sys


def summarize(folder: Path) -> dict:
    rows = []
    for path in sorted(folder.iterdir(), key=lambda item: item.name):
        info = path.lstat()
        if stat.S_ISREG(info.st_mode):
            rows.append({"name": path.name, "bytes": info.st_size})
    return {
        "files": rows,
        "total_bytes": sum(row["bytes"] for row in rows),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Summarize immediate files.")
    parser.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    try:
        result = summarize(args.folder)
    except OSError as exc:
        print(f"Cannot summarize folder: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 8.2 How it works

`argparse` supplies argument parsing and help. `Path` represents a filesystem path. `iterdir()` visits immediate children; `lstat()` reads metadata for the entry itself instead of following a symbolic link. The regular-file check excludes directories and symbolic links. Sorting makes output easier to compare between runs.

`summarize()` collects data. `main()` handles command-line input, user-visible errors, and serialization. `SystemExit` communicates the final status to the shell. JSON uses ASCII escaping here so filenames outside a terminal's encoding can still be represented.

The output reports logical file sizes, not allocated disk space. A directory can change during scanning; a removed or inaccessible entry makes this version fail rather than silently issue a partial report. It is not a security scanner, atomic snapshot, recursive inventory, or special Windows reparse-point policy engine.

### 8.3 Run it

Create a folder named `sample` containing only `a.txt` with the exact three bytes `abc`. Run from the project folder:

```powershell
.\.venv\Scripts\python.exe file_summary.py sample
```

Linux:

```bash
.venv/bin/python file_summary.py sample
```

The result should contain one row named `a.txt` with `bytes` equal to `3`, and `total_bytes` equal to `3`. A text editor that adds a newline will change the size; that is a useful first debugging exercise.

### 8.4 Tests

Save beside it as `test_file_summary.py`:

```python
import tempfile
from pathlib import Path
import unittest

from file_summary import summarize


class SummaryTests(unittest.TestCase):
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(summarize(Path(tmp)),
                             {"files": [], "total_bytes": 0})

    def test_counts_files_and_skips_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "b.txt").write_bytes(b"four")
            (root / "a.txt").write_bytes(b"abc")
            (root / "nested").mkdir()
            (root / "nested" / "ignored.txt").write_bytes(b"ignored")
            self.assertEqual(summarize(root), {
                "files": [{"name": "a.txt", "bytes": 3},
                          {"name": "b.txt", "bytes": 4}],
                "total_bytes": 7,
            })

    def test_missing_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                summarize(Path(tmp) / "missing")


if __name__ == "__main__":
    unittest.main()
```

Run with your environment's Python and `-m unittest -v`. No third-party testing package is required. These tests use temporary invented files and check behavior, not private project data.

### 8.5 Extend it yourself

Add an optional minimum size, human-readable output alongside JSON, and a choice between failing immediately or returning partial results with explicit errors. Before adding recursion, define what happens with links, permission failures, cycles, changing directories, and very large trees.

**Checkpoint:** rebuild this tool from its requirements without copying the implementation. Then add one feature and one meaningful failure test independently.

## 9. Git and engineering workflow

### 9.1 The model

Git stores project history as commits. Your working tree is the current files. The staging area selects the next snapshot. A branch is a movable name for a commit. A remote is a configured repository location, not automatic cloud backup of every local file.

In a new practice project, after creating your files:

```text
git init
git status
git add file_summary.py test_file_summary.py
git diff --staged
git commit -m "Add file summary tool and behavior tests"
git switch -c feature/minimum-size
```

Set your Git author identity if prompted, using the identity you intend to associate with commits. Review changes before committing. Explicit file paths help avoid accidentally including environments or private files.

### 9.2 Learn these workflows

- `git diff`: inspect edits before recording them.
- `git log`: inspect history.
- Branches and merges: develop a change separately and integrate it.
- Conflict resolution: understand both edits and test the combined result.
- `git revert`: create a new commit reversing a previous commit.
- `git bisect`: narrow down the commit that introduced a reproducible failure.
- Remotes and pull requests: exchange changes and review reasoning.

Learn destructive history operations in a disposable practice repository first. `.gitignore` does not remove a secret already committed. If a real secret enters history, revocation or rotation is part of recovery.

### 9.3 A small professional project

```text
file-summary/
  README.md
  file_summary.py
  test_file_summary.py
  .gitignore
  docs/
    decisions.md
```

The README explains purpose, prerequisites, installation, commands, tests, and limitations. `decisions.md` records important choices and why they fit the problem. Exclude virtual environments, build products, credentials, and unnecessary local data from version control.

**Exercise:** deliberately make two branches change the same output message, merge them, resolve the conflict, and explain the final behavior. Use [Pro Git](https://git-scm.com/book/en/v2) for the concepts and workflows.

## 10. Algorithms, data structures, and mathematics

### 10.1 Choosing how to store data

- **Array/list:** ordered items; good for iteration and indexed access.
- **Hash map/dictionary:** associates a key with a value; good for counts and lookups.
- **Set:** tracks distinct values and membership.
- **Stack:** last-in, first-out; useful for undo or depth-first exploration.
- **Queue:** first-in, first-out; useful for work scheduling.
- **Heap:** efficiently retrieves an item with highest or lowest priority.
- **Tree:** expresses hierarchy or ordered indexing.
- **Graph:** expresses relationships such as dependencies and routes.

Example: to count repeated filenames, a dictionary avoids comparing every name against every previous name. To process jobs fairly in arrival order, use a queue. The domain should explain the structure you choose.

### 10.2 Complexity

Big-O describes how resource use grows with input size. It does not predict exact execution time.

- `O(1)`: roughly fixed work with respect to the measured input size.
- `O(log n)`: repeatedly shrinking a search region, such as binary search.
- `O(n)`: one full pass.
- `O(n log n)`: common efficient comparison sorting.
- `O(n²)`: comparing many pairs.

Scanning 1,000 versus 1,000,000 records can turn a harmless nested loop into a serious problem. But disk access, constants, caching, and implementation still matter. Measure actual workloads before optimizing.

### 10.3 Correctness tools

Learn invariants: conditions that should stay true throughout an operation. For a bounded queue, `0 <= size <= capacity` is an invariant. For a balance transfer, the sum of the balances should remain constant if fees are absent.

Practice boundary cases: zero items, one item, duplicates, very large input, invalid encoding, and unexpected order. Recursion requires a base case and progress toward it.

### 10.4 Exercises

Implement a frequency counter, binary search, a stack-based bracket checker, breadth-first search over a small graph, and an LRU cache. Explain each operation's expected complexity. Compare a deliberately slow duplicate detector with a set-based version on increasing input sizes.

For applications, add statistics basics: averages, medians, percentiles, variation, sampling bias, and correlation versus causation. A median response time can look good while the slowest users experience severe delays.

## 11. C, memory, compilation, and linking

### 11.1 Why learn C

C exposes mechanisms often hidden by high-level languages: bytes, pointers, object lifetimes, memory layout, and explicit resource management. It is valuable for understanding operating systems, native libraries, binary interfaces, and performance.

Learn declarations, functions, arrays, structs, pointers, strings, headers, allocation, and error handling. C strings conventionally end with a zero byte; a pointer alone does not carry a buffer's length.

### 11.2 A complete example

Save as `sum.c`:

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 3;
    int *values = malloc(count * sizeof *values);
    if (values == NULL) {
        fputs("Allocation failed\n", stderr);
        return 1;
    }

    values[0] = 10;
    values[1] = 20;
    values[2] = 30;
    int total = 0;
    for (size_t i = 0; i < count; ++i) {
        total += values[i];
    }
    printf("%d\n", total);
    free(values);
    return 0;
}
```

Expected output: `60`. `malloc` obtains storage; its contents are initially uninitialized. The pointer identifies that storage. The loop visits only valid indexes. `free` releases it; accessing it afterward would be invalid. Production code deriving allocation sizes from input must also check size overflow and reasonable limits.

Linux GCC:

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -g sum.c -o sum
./sum
```

Windows, in a **Developer PowerShell for Visual Studio** with the C++ toolchain installed:

```powershell
cl /std:c17 /W4 /Zi sum.c /Fe:sum.exe
.\sum.exe
```

The developer shell supplies compiler and SDK environment settings. An ordinary PowerShell session may not locate `cl`.

### 11.3 The build pipeline

Preprocessing handles directives such as includes. Compilation translates source into lower-level representations. Assembly produces object code. Linking connects definitions and references across object files and libraries. At runtime, the loader maps the executable and needed shared libraries into a process.

A compiler error and a linker error indicate different stages. “Unknown type” often concerns declarations. “Unresolved external symbol” often means a referenced implementation was not linked or its signature does not match.

### 11.4 Important memory distinctions

Automatic local objects typically use stack storage. Dynamically allocated objects use allocated storage commonly called the heap. Static objects have program-long storage duration. These are useful mental models, but optimize-aware compilers may change physical placement while preserving required behavior.

Learn buffer overruns, use-after-free, double-free, uninitialized reads, alignment, integer conversion, and undefined behavior. Undefined behavior is not a guaranteed crash; it can produce apparently correct behavior until the compiler or input changes.

For a Linux development build, try supported sanitizers:

```bash
gcc -std=c17 -Wall -Wextra -g -fsanitize=address,undefined sum.c -o sum-checked
./sum-checked
```

Sanitizers detect classes of failures in executed paths. They are not proof that unexecuted paths are correct.

**Checkpoint:** compile and debug a small C program, explain pointer versus pointed-to value, and fix a deliberately introduced off-by-one error in your practice code.

## 12. C++, Rust, C#, and choosing languages

You do not need every language before building. Use Python for initial automation, C for machine-level understanding, and choose a main project language based on the software you want to make.

### 12.1 C++

C++ is useful for native applications, libraries, graphics, games, and performance-sensitive systems. Study references, value semantics, constructors/destructors, RAII, standard containers, smart pointers, templates, and move semantics.

**RAII** binds resource lifetime to object lifetime. For example, a lock guard releases its lock when its scope ends, including when an exception unwinds the stack. Prefer standard containers and clear ownership over scattered manual allocations. Learn C++ as its own language rather than merely writing C with classes.

**Exercise:** reimplement File Summary with `std::filesystem`. Return errors intentionally, define link behavior, and compare output against the Python version.

### 12.2 Rust

Rust emphasizes ownership and borrowing. A value has an owner; references borrow access under rules that prevent many memory-lifetime and data-race problems in safe code. Learn `Option`, `Result`, pattern matching, traits, collections, and Cargo before advanced lifetimes or asynchronous runtimes.

Rust does not automatically eliminate deadlocks, application authorization mistakes, memory leaks, or every error in unsafe code. Its guarantees address specific classes of bugs.

**Exercise:** write a line-counting CLI that reports I/O errors using `Result`. Then add tests and compare behavior on files with and without a trailing newline. Start with [The Rust Programming Language](https://doc.rust-lang.org/book/).

### 12.3 C# and .NET

C# is a strong route into Windows applications, services, and cross-platform .NET backends and tools. Learn types, classes, interfaces, generics, collections, exceptions, LINQ, `IDisposable`, and `async`/`await`.

With a supported .NET SDK installed, inside a fresh practice folder:

```text
dotnet new console -n HelloDev
dotnet run --project HelloDev
```

Inspect the generated project file and program. The SDK is needed to build; deployed applications may require a runtime unless published in a suitable self-contained form. See the [.NET console tutorial](https://learn.microsoft.com/en-us/dotnet/core/tutorials/create-console-app?pivots=vscode).

### 12.4 Additional languages when they solve a problem

JavaScript/TypeScript serve browser applications. SQL queries relational data. Go is useful for network services and infrastructure tools. Java is relevant to large server ecosystems and some desktop/mobile work. Assembly becomes useful for architecture, debugging, and low-level specialization.

Choose one primary language for each substantial project. Changing languages will not solve unclear requirements or missing tests.

## 13. Operating-system internals

### 13.1 Processes, threads, and scheduling

A process owns an execution environment, address space, and resources. Threads execute within a process and share much of its memory. The scheduler decides which runnable threads get CPU time.

A program can exist as a file without running. Starting it creates one or more processes; a process can create multiple threads. Several programs can appear to run simultaneously on one core because the OS switches between them.

**Experiment:** run a program that sleeps, then inspect it in Task Manager or `ps`. Compare elapsed time and CPU consumption. Waiting for time to pass is different from continually performing calculations.

### 13.2 Virtual memory

Programs use virtual addresses. The OS and hardware map these to physical memory and enforce access rules. Paging allows granular mappings; page faults occur when a requested mapping needs attention. Not every page fault means data was fetched from disk.

Memory use is not one number. Reserved address space, committed memory, resident pages, mapped files, and shared pages answer different questions. Before calling something a leak, identify which measure is growing and whether it should shrink.

### 13.3 System calls and privilege

User programs request protected operations through OS interfaces. A library call may perform one or more system calls, or none. User mode limits direct privileged operations; kernel mode has broader authority.

A permission failure might arise from filesystem permissions, access tokens, mandatory access controls, sandboxing, or a resource policy. “Run as administrator” can conceal the real design problem.

### 13.4 Concurrency

A race occurs when results depend on uncontrolled timing. A data race concerns conflicting unsynchronized memory access under a language's rules. Deadlock occurs when work waits in a cycle that cannot progress.

If two workers both read a counter as 5, both add 1, and both write 6, one update is lost. A lock, atomic operation, or message-passing design can address the problem depending on context.

Learn mutexes, condition variables, semaphores, atomics, queues, cancellation, and backpressure. **Backpressure** prevents producers from creating work faster than consumers can safely process it.

Asynchronous I/O lets execution proceed while an operation waits; it does not guarantee parallel CPU execution. Thread pools need bounds, timeouts, and shutdown behavior.

### 13.5 Filesystems and persistence

Study metadata, allocation, caching, journaling, buffering, synchronization, rename semantics, and crash consistency. A successful write into a buffer is not necessarily durable storage after sudden power loss.

An “atomic save” commonly writes a temporary file and replaces a target, but durability and replacement guarantees depend on filesystem, platform, and synchronization details. Use a transactional database where its guarantees fit your data better.

**Read:** [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/). Use its exercises to connect mechanisms with observable behavior.

**Checkpoint:** explain a process versus a thread, why a race loses data, and why a successful buffered write does not necessarily mean durable data.

## 14. Linux systems development

### 14.1 Interfaces to learn

Study file descriptors; `open`, `read`, `write`, and `close`; process creation and execution; `wait`; signals; pipes; sockets; polling; memory mapping; and thread synchronization.

A file descriptor is a small process-local integer referring to an open resource. File descriptors 0, 1, and 2 conventionally represent standard input, output, and error. A short read or write can be valid; robust code loops until the intended operation is complete or a defined stopping condition occurs.

`fork` creates a child process with a related initial state; an `exec` function replaces the calling process image. Learn how descriptors and environment pass to children, and why the parent must reap terminated children.

### 14.2 Observe before guessing

In a practice Linux environment:

```bash
ps -ef
df -h
du -sh .
strace -o trace.txt /usr/bin/printf 'hello\n'
less trace.txt
```

`strace` records system-call activity where permitted. Compare application output with calls related to loading, writing, and exit. Trace files can contain application data, so use fictional inputs when learning.

Learn `/proc`, `/sys`, `lsof` when installed, and debugging with GDB. `/proc` exposes process and kernel information; `/sys` exposes structured device/kernel information. These are interfaces, not ordinary persistent documents.

### 14.3 Services and startup

On a Linux environment running systemd, inspect services with `systemctl` and logs with `journalctl`. Other init systems exist. WSL configuration may affect availability.

Your first long-running application should work in the foreground before becoming a service. Then define its executable, working directory, environment, account, restart policy, log handling, and shutdown behavior.

**Exercise:** make a worker that processes fictional queue entries, handles termination gracefully, and restarts without duplicating completed work. Install it as a user service in a disposable Linux lab only after foreground behavior is verified.

### 14.4 Build toward systems expertise

Implement a file-copy tool that handles short writes, a pipeline runner, a local socket service, and a bounded worker pool. Study namespaces, cgroups, capabilities, and mandatory access controls after basic process and permission work.

Use [The Linux Programming Interface](https://man7.org/tlpi/) for system-programming depth, and current manual pages for the exact APIs on your installed system. Older books explain enduring mechanisms but do not establish current support for every API or behavior.

## 15. Windows systems development

### 15.1 The Windows mental model

Learn processes and threads, handles, access tokens, security identifiers, objects, virtual memory, DLLs, the Registry, services, and event tracing. A handle is an opaque reference to a resource, not a portable Unix file descriptor.

Win32 exposes many user-mode OS interfaces. A function's error contract matters: some return an error code directly; some use a failure return and `GetLastError`; other APIs use HRESULT values. Follow the function's documentation rather than applying one error rule everywhere.

Native Windows APIs commonly expose UTF-16 “wide” string interfaces. Language runtimes may hide conversions. Do not assume a narrow string represents every user's filename correctly.

### 15.2 Tools

- **Visual Studio debugger:** breakpoints, stepping, call stacks, watches, and native/managed debugging.
- **WinDbg:** advanced native and crash-dump investigation.
- **Process Explorer:** inspect process relationships and resources.
- **Process Monitor:** investigate filesystem, Registry, and process activity.
- **Event Viewer:** inspect recorded system/application events.
- **Windows performance tools:** investigate traces, CPU use, and waiting when simple measurements are insufficient.

Obtain diagnostic tools through [Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/). Begin by observing a small program you wrote, so you can connect each action to its effects.

### 15.3 Practical progression

1. Write a C# console tool and a native C/C++ console tool.
2. Read and write files using correct path and encoding handling.
3. Launch a child process, capture its result, and enforce a timeout.
4. Observe opened files or DLL loading using diagnostic tools.
5. Create a background worker with graceful cancellation.
6. Learn service installation and account configuration in a Windows VM.
7. Investigate a deliberately crashed practice program with matching symbols.

### 15.4 Services, COM, and integration

A Windows service runs under the Service Control Manager and must cooperate with start/stop expectations. It may run without a signed-in user and should not depend on interactive desktop prompts.

COM is an interface-based component system used by many Windows APIs. Learn interface contracts, reference counting, and apartment/threading rules when a project requires it. P/Invoke allows managed code to call native functions; incorrect type layout or ownership can cause severe failures.

For depth, use [Windows Internals](https://learn.microsoft.com/en-us/sysinternals/resources/windows-internals). For app framework selection, use [Microsoft's Windows development paths](https://learn.microsoft.com/en-us/windows/apps/get-started/).

**Checkpoint:** trace a file access, identify the identity running your process, explain a handle leak, and distinguish application exceptions from OS access failures.

## 16. Networking and protocols

### 16.1 A request's journey

A client resolves a hostname through DNS, chooses an address, establishes communication, and exchanges messages under an agreed protocol. HTTPS additionally uses TLS to protect the connection and authenticate the server through certificates.

- **IP address:** identifies a network interface/addressable endpoint within routing context.
- **Port:** distinguishes transport endpoints on a host.
- **TCP:** reliable ordered byte stream; it does not preserve application message boundaries.
- **UDP:** datagrams; applications must accommodate loss, duplication, or reordering where relevant.
- **DNS:** maps names to records, including addresses.
- **HTTP:** request/response semantics used by web applications and APIs.
- **TLS:** protects transport confidentiality and integrity when correctly configured and verified.

### 16.2 Local server experiment

Create an empty practice folder with a harmless `index.html`, then run your environment's Python using these arguments:

```text
python -m http.server 8000 --bind 127.0.0.1
```

Replace `python` with the correct Linux or Windows interpreter command. Open `http://127.0.0.1:8000` in a browser. Stop with Ctrl+C. This development server exposes files in its served directory; keep the experiment in the intended sample folder. It is not your production application server.

Loopback addresses such as `127.0.0.1` refer to the local networking context. Binding to all interfaces changes reachability; it does not automatically configure firewalls, routers, or container port mappings.

### 16.3 Inspect requests

Windows PowerShell:

```powershell
Test-NetConnection 127.0.0.1 -Port 8000
Invoke-WebRequest http://127.0.0.1:8000
```

Linux with curl installed:

```bash
curl -i http://127.0.0.1:8000
ss -ltn
```

Distinguish DNS failure, connection refusal, timeout, TLS failure, and an HTTP error response. A `404` means an HTTP server responded; it is different from failing to reach the server.

### 16.4 Robust protocol design

For a TCP chat protocol, define message framing: perhaps a length prefix or newline-delimited records. One receive call may contain half a message or multiple messages. Impose message-size limits and timeouts.

Retries need limits and backoff. Retrying a read is different from retrying a payment-like state change. An idempotency key can identify a repeated logical request so it is not applied twice.

Learn HTTP methods, headers, status codes, cookies, caching, authentication, CORS, proxies, WebSockets, IPv4/IPv6, routing, NAT, and firewalls in that order as projects need them.

**Exercise:** inspect a request in browser developer tools, identify method/status/headers/body, and explain where each part originated. Later build a framed local TCP echo service using [Beej's Guide](https://beej.us/guide/bgnet/).

## 17. SQL, databases, and persistent data

### 17.1 Choose storage by the problem

Plain files suit simple exports and configuration. SQLite suits many local applications and small tools. A server database such as PostgreSQL suits applications needing a separate database service and more concurrent access patterns. A cache is not automatically the authoritative store.

Learn tables, rows, types, primary keys, foreign keys, constraints, joins, indexes, transactions, and schema migrations before adding an object-relational mapper.

### 17.2 Complete SQLite example

Save as `tasks_demo.py` in a practice folder:

```python
import sqlite3

connection = sqlite3.connect(":memory:")
try:
    connection.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL CHECK(length(trim(title)) > 0),
            done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1))
        )
    """)
    with connection:
        connection.execute("INSERT INTO tasks(title) VALUES (?)",
                           ("Build my first CLI",))
    rows = connection.execute(
        "SELECT id, title FROM tasks WHERE done = ? ORDER BY id", (0,)
    ).fetchall()
    print(rows)
finally:
    connection.close()
```

Expected output: `[(1, 'Build my first CLI')]`. The in-memory database disappears when closed. To practice persistence later, deliberately choose a new database filename. Parameters keep values separate from SQL syntax; do not interpolate user text into SQL strings.

The transaction context commits a successful block and rolls back on failure. Closing the connection is handled separately. Database constraints remain important even if your UI already checks input.

### 17.3 Data design and migrations

An index can reduce lookup work but costs storage and write maintenance. Use a query plan to check whether an index helps the actual query. A migration is a versioned change to schema or data; test it on a copy and consider compatibility with the application being deployed.

Foreign keys express relationships; SQLite applications must enable foreign-key enforcement per connection when relying on it. Store timestamps under an explicit timezone convention, and define how users' local times are interpreted.

For backups, use the database's supported backup mechanism or a controlled shutdown/copy procedure. Copying a live database's main file alone may miss related state.

### 17.4 Advanced data skills

Learn isolation, lost updates, locking, connection pools, pagination, query planning, replication, and recovery objectives. Two users editing the same task require an explicit conflict policy, such as comparing an expected version before updating.

**Exercise:** build a task database, add tags through a relation, write a join, add a migration, and restore a backup into a new location. Continue with the [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html).

## 18. Web applications and APIs

### 18.1 The pieces

HTML describes content and structure. CSS controls presentation. JavaScript supplies browser behavior. A backend receives requests, validates input, applies business rules, and accesses data. A database persists state.

The browser is controlled by the user. Hiding a button is not authorization; the server must enforce permission on the request itself.

### 18.2 A complete browser exercise

Save as `index.html` and open it in a browser:

```html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Practice task</title>
<main>
  <h1>Practice task</h1>
  <form id="task-form">
    <label for="title">Task title</label>
    <input id="title" name="title" required maxlength="120">
    <button type="submit">Preview</button>
  </form>
  <p id="preview" aria-live="polite"></p>
</main>
<script>
  const form = document.querySelector("#task-form");
  const title = document.querySelector("#title");
  const preview = document.querySelector("#preview");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = title.value.trim();
    preview.textContent = value ? `Task: ${value}` : "Enter a task title.";
  });
</script>
</html>
```

The label names the input for users and assistive technology. `preventDefault()` keeps the demonstration local. `textContent` displays supplied text without treating it as HTML. Refreshing loses the preview: there is no persistence or backend yet.

### 18.3 Add the backend in stages

Choose one framework: for example a Python framework or ASP.NET Core. Learn the maintained framework tutorial matching your chosen version.

1. Add `GET /health` returning a small JSON result.
2. Add `GET /tasks` backed by a test database.
3. Add `POST /tasks` with server-side validation and a clear response contract.
4. Add editing and deletion with explicit ownership rules.
5. Add migrations and integration tests.
6. Add authentication using maintained framework facilities.
7. Add deployment configuration, logging, and backup/restore procedures.

**API design exercise:** decide how `POST /tasks` responds to missing title, whitespace-only title, malformed JSON, oversized body, database failure, and repeated submission. A successful happy-path response is only part of the contract.

### 18.4 Topics to learn next

Promises, `async`/`await`, fetch requests, modules, semantic HTML, responsive layout, accessibility, forms, cookies, CSRF defenses, CORS, sessions, pagination, uploads, rate limits, and background jobs.

CORS is a browser cross-origin access mechanism; it is not an authentication system. A server still needs to authorize requests from non-browser clients.

Use [MDN's web curriculum](https://developer.mozilla.org/en-US/docs/Learn_web_development). Build a small application using ordinary HTML and JavaScript before adding a large frontend framework.

## 19. Desktop applications and user interfaces

### 19.1 Choose by platform needs

For Windows-specific C# applications, evaluate WPF, Windows Forms, or WinUI using current Microsoft guidance and your UI requirements. They have different histories, deployment models, and capabilities. For native cross-platform applications, investigate Qt; for Linux-native desktop work, GTK is another route. A browser-based desktop shell introduces a different runtime and packaging tradeoff.

A cross-platform language does not make every UI framework cross-platform. In particular, WPF and Windows Forms are Windows UI technologies even though modern .NET has cross-platform components.

### 19.2 Understand the event loop

A UI receives events such as clicks, keystrokes, resize requests, and completed work. If a click handler performs a long blocking operation, the UI may stop responding. Move appropriate work off the UI thread and marshal updates through the framework's supported mechanism.

Cancellation is part of the design. If a user closes a window during a file scan, decide whether work stops, continues safely, or asks for a choice. Do not let a background worker access already-destroyed UI state.

### 19.3 Structure a desktop project

Keep domain logic independent of windows and widgets. A task repository manages stored tasks; a view displays tasks; a controller or view model coordinates actions. This permits testing the logic without launching the entire UI.

Design empty, loading, success, and error states. Preserve unsaved work deliberately. Learn keyboard navigation, focus order, high-DPI behavior, accessible names, screen-reader use, and contrast.

**Project exercise:** wrap File Summary in a desktop window. Add folder selection, progress, cancellation, and JSON export. Verify it stays responsive during a large scan and reports inaccessible files honestly.

## 20. Testing, debugging, and performance

### 20.1 A practical testing strategy

- **Unit tests:** check small rules in isolation.
- **Integration tests:** check components working together, such as repository code and a real temporary database.
- **End-to-end tests:** check a complete user journey.
- **Contract tests:** verify agreed behavior between components.
- **Property-based tests:** generate inputs and check invariants.
- **Fuzz tests:** explore malformed or unexpected inputs, especially parsers.
- **Regression tests:** preserve the behavior fixed by a discovered bug.

Use test doubles at expensive or unreliable boundaries, but still run some real integration tests. A suite that replaces every dependency with a fake cannot establish that the real system connects correctly.

### 20.2 Debugging workflow

1. Reproduce the issue with exact inputs and versions.
2. Reduce it to the smallest failing example.
3. Read the whole error and identify the first relevant failure.
4. Form one hypothesis.
5. Inspect with logs or a debugger.
6. Change one cause and rerun the reproduction.
7. Add a regression test where appropriate.
8. Record the cause and the verified fix.

Learn stepping into/over functions, call stacks, conditional breakpoints, watches, and exception breakpoints. Debug symbols connect machine code to source locations; keep matching symbols for native crash investigation.

### 20.3 Performance method

State the goal in measurable terms: “scan 10,000 small files within an agreed time on the test machine,” rather than “make it fast.” Measure CPU time, wall time, memory, I/O, throughput, and tail latency as relevant.

Profile before changing algorithms. If the program waits on disk, rewriting arithmetic in C may achieve little. If most time is in repeated database queries, batching or a better query can help more than extra threads.

Record input size, hardware, versions, warm/cold cache conditions, and multiple runs. Comparing different workloads gives misleading results.

### 20.4 Reliability tests

Try interrupted writes, missing files, full disks in a controlled VM, port conflicts, unavailable dependencies, slow requests, and shutdown while work is pending. Set bounds so a failure test cannot run forever.

**Checkpoint:** diagnose one functional bug, one resource leak or retained-resource problem, and one measured bottleneck. Use [Systems Performance](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) when you are ready for deeper investigation.

## 21. Security engineering

### 21.1 Begin with a threat model

Identify what you protect, who may access it, what inputs are untrusted, and where authority changes. A local personal tool and an internet-facing multi-user service have different exposure and permission needs.

Example: a task app stores private notes. One user must not obtain another user's notes by changing an ID in a request. The server must check ownership, not merely whether the caller is logged in.

### 21.2 Essential distinctions

- **Authentication:** establish identity.
- **Authorization:** decide what that identity may do.
- **Encryption:** protect confidentiality with keys.
- **Hashing:** compute a digest; ordinary fast hashes are not password-storage schemes.
- **Validation:** determine whether input meets a contract.
- **Encoding:** represent data safely for a specific output context.

Use maintained password-hashing facilities and framework authentication mechanisms. Do not invent cryptographic protocols or place secrets in source files. Store credentials using an appropriate local or hosted secret mechanism; keep them out of logs and error pages.

### 21.3 Common failure patterns

SQL injection comes from mixing untrusted text with query syntax; use parameters. Command injection comes from treating data as shell code; use direct process argument APIs when possible. Cross-site scripting comes from unsafe interpretation of data as browser code; use the framework's contextual escaping. Path traversal comes from allowing a supplied path to escape intended storage boundaries.

Uploads need size, type, storage, and processing limits. A file extension alone is not validation. Authorization must cover downloads and exports as well as ordinary pages.

### 21.4 Dependencies and delivery

Track dependencies, review security advisories, update deliberately, and test changes. Locking a version improves repeatability but does not make that version safe. Code signing proves something about publisher identity and integrity under its trust model; it does not prove the program is bug-free.

Learn least privilege, secure defaults, TLS verification, session expiry, CSRF defenses where relevant, and audit events. Exercise security skills on systems you own or are authorized to test.

**Exercise:** write five abuse cases for your application and a test for each enforceable rule. Start with the [OWASP Cheat Sheet Series](https://owasp.org/www-project-cheat-sheets/) for topic-specific implementation guidance.

## 22. Build systems, packaging, and releases

### 22.1 Build versus run versus release

Source code is the input. Build tools produce runnable artifacts. Packaging assembles the artifact with metadata and required resources. Releasing makes a version available under a documented support and upgrade plan.

Learn dependencies, compiler flags, debug/release configuration, generated files, static/shared linking, artifact architecture, and runtime requirements. A successful build on your laptop is not proof the release works on another machine.

### 22.2 Minimal CMake project

Put `sum.c` from chapter 11 beside this `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.20)
project(SumDemo LANGUAGES C)
add_executable(sum sum.c)
set_target_properties(sum PROPERTIES
    C_STANDARD 17
    C_STANDARD_REQUIRED YES
    C_EXTENSIONS NO
)
```

With CMake and a compatible compiler installed:

```text
cmake -S . -B build
cmake --build build --config Debug
```

Executable location depends on the generator: it may be `build/sum` or a configuration subdirectory such as `build/Debug/sum.exe`. Configure separate build folders for different platforms, compilers, or architectures. Never share a generated Windows build directory as a Linux build directory.

Reference: the [CMake documentation](https://cmake.org/documentation/). Check the tutorial matching your installed version when moving beyond this basic example.

### 22.3 Packaging by ecosystem

Python projects use declared metadata and distributable packages; native extensions require platform considerations. .NET offers framework-dependent and self-contained publishing. Native Windows apps may use installers or MSIX where suitable. Linux applications may use distribution packages or other delivery formats appropriate to their audience.

Choose one packaging route for your first release. Define install location, user data location, uninstall behavior, configuration, and update strategy. Do not delete user-created data merely because an application is uninstalled.

### 22.4 Continuous integration

CI runs automated checks on a clean environment after changes. Your first pipeline should install declared dependencies, run tests, and build an artifact. Add both Windows and Linux jobs for a cross-platform project.

Later add formatting/lint checks, dependency review, integration tests, signed releases where appropriate, and artifact retention. Restrict deployment credentials to the jobs that need them. A passing Linux job does not establish Windows compatibility.

**Checkpoint:** produce a release from a clean checkout using only documented steps, then test installation and upgrade in a clean environment.

## 23. Containers, virtual machines, and cloud

### 23.1 The distinctions

A virtual machine runs a guest operating system on virtualized hardware. A container packages a process environment using host-kernel isolation mechanisms. An image is the template; a container is a running instance; a volume stores data with a lifecycle separate from a disposable container.

Linux containers on Windows normally require a Linux kernel environment, such as the one provided by a VM/WSL backend. Windows containers have their own compatibility requirements. A container does not make an arbitrary Linux executable become a native Windows program.

### 23.2 Learning progression

First run your application directly. Next describe its dependencies, configuration, listening port, and persistent data. Then containerize it and verify that restart/recreation preserves the intended state.

Learn image layers, build context, `.dockerignore`, explicit runtime users, port mappings, health checks, persistent volumes, and logs. Use maintained base images; record tested versions and update them deliberately. Check current desktop-product licensing when relevant to your use.

Use the [Docker getting-started documentation](https://docs.docker.com/get-started/). Add a database container only after you understand how its data survives recreation.

### 23.3 Cloud fundamentals

Study virtual machines, virtual networks, identity/access management, object storage, managed databases, DNS, load balancers, and monitoring. Choose one provider to practice, then learn the concepts behind its product names.

Estimate spending, configure available budget alerts, and remove unneeded resources after experiments. Alerts are not necessarily hard spending caps. Record where state lives before deleting an environment.

### 23.4 When orchestration is useful

Orchestration systems manage many workloads and their placement, configuration, and recovery. Learn them after you can deploy and debug a single service. Kubernetes is a specialization tool, not a prerequisite for your first application.

**Exercise:** run a containerized practice app, recreate its container, verify persistence, and explain the difference between image contents, configuration, and volume data.

## 24. Operations, reliability, and recovery

### 24.1 Your program after release

Development continues after installation. Users encounter changing permissions, unavailable networks, corrupted input, full disks, and version upgrades. Good software makes these states understandable and recoverable.

Maintain structured logs, useful error messages, metrics, and health checks. Log enough to identify a request or job, but avoid collecting secrets or unnecessary private content.

### 24.2 Reliability vocabulary

- **SLI:** measured service behavior, such as successful-request proportion.
- **SLO:** a target for that measure over a defined period.
- **RPO:** acceptable amount of lost data measured in time.
- **RTO:** acceptable time to restore service.
- **Runbook:** instructions for an operational task or failure.

For a personal notes app, you might choose a daily backup and a restore procedure you can finish in an hour. Those are example design targets, not guarantees provided by a tool.

### 24.3 Backup and restore

A backup exists independently of the failure it protects against. A second file on the same failing drive does not protect against drive loss. Synchronization can propagate accidental deletion, so it is not automatically a historical backup.

Restore into a separate location and verify actual records or files. Record the procedure, required credentials, and measured recovery time without placing secret values in the runbook.

### 24.4 Deployment changes

Plan compatibility between old/new code and database schema. A code rollback cannot necessarily undo a destructive migration. Prefer staged, reversible changes when practical, and test data transformations on copies.

**Exercise:** release version 1, create sample data, upgrade to version 2, simulate a failed startup, and recover. Document what remained intact and what you had to restore.

## 25. Architecture and designing from scratch

### 25.1 Start with a problem statement

Example: “I need to locate large files in a selected folder and export a report.” Clarify who uses it, what success looks like, expected data size, platforms, and failure consequences.

Avoid beginning with a list of frameworks. Identify the smallest useful end-to-end result first.

### 25.2 A repeatable design process

1. Write three concrete user stories.
2. Define inputs, outputs, and failure cases.
3. Identify authoritative data and where it lives.
4. Sketch modules and boundaries.
5. Select the smallest reasonable technology stack.
6. Implement one complete path from input to visible result.
7. Test critical rules and failures.
8. Add packaging and reproducible setup.
9. Get feedback from actual use.
10. Improve the design based on observed problems.

For File Summary, modules might be scanning, filtering, formatting, and UI. For a task app, they might be task rules, persistence, HTTP/UI adapters, and configuration.

### 25.3 Principles that matter

**Cohesion:** keep related responsibilities together. **Coupling:** avoid unnecessary dependence between modules. **Encapsulation:** expose a stable interface while hiding details. **Dependency inversion:** let core rules depend on an abstraction when interchangeable external implementations are actually needed.

Example: a task rule should accept a repository interface if tests and production need different storage implementations. Do not add five abstraction layers for a script with one calculation and one file.

### 25.4 Document tradeoffs

For each important decision, record context, choice, alternatives, and consequences. “SQLite keeps the local app easy to install; a multi-user hosted edition may need a different concurrency model” is more useful than “SQLite is best.”

Learn architecture through a modular single application before splitting it into services. Distributed boundaries add network failure, deployment coordination, and data-consistency problems.

**Checkpoint:** design a small project on one page, build its smallest useful version, and explain why every component exists.

## 26. Cross-platform engineering

### 26.1 Differences you must test

- Filesystem case rules, separators, reserved names, path length, and links.
- Text encoding, terminal encoding, and newline conventions.
- Permissions, administrator/root assumptions, and service identities.
- File sharing, locking, rename, and deletion behavior while files are open.
- Process creation, signals, exit statuses, and cancellation.
- Environment variables, executable discovery, and working directory.
- Available native libraries, CPU architecture, and ABI compatibility.
- UI behavior, fonts, scaling, keyboard conventions, and accessibility.
- Timezones, locale-specific formatting, and sorting.
- Installation, updates, and user-data directories.

### 26.2 Design for portability

Keep portable business rules in one layer and platform integrations in small adapters. Use standard path, subprocess, time, and networking APIs where they meet your requirements. Pass arguments as a list rather than constructing a shell command from user data.

Define cancellation as a program-level contract rather than assuming identical Unix signals and Windows control events. Use temporary directories supplied by the platform, not hardcoded `/tmp` or a particular drive letter.

### 26.3 A compatibility test set

For each release test:

1. A path with spaces and non-ASCII characters.
2. A fresh directory and an empty input.
3. A missing file and permission failure.
4. Invocation from outside the project directory.
5. Output redirected to a file.
6. Clean installation without developer tools unless explicitly required.
7. Shutdown during work.
8. Upgrade preserving user data.

Add architecture-specific builds only when supported and tested. “Works on my x64 Windows laptop” does not establish ARM64 or Linux compatibility.

**Checkpoint:** make two clean checkouts, run the same behavioral tests on both platforms, and explain every intentional difference.

## 27. Adjacent domains and specialization routes

This is the broader map. Each route assumes the foundations above and points toward a concrete first project. These are introductions and entry requirements, not claims that one chapter confers specialist expertise.

### 27.1 Kernel and driver development

**Prerequisites:** strong C, pointers, concurrency, OS internals, architecture, debugging, and build tools.

Learn interrupts, privileged execution, device I/O, DMA, synchronization constraints, memory ordering, and user/kernel boundaries. Kernel code can affect the entire OS, so work in disposable VMs or dedicated hardware with a recovery method.

**First project:** modify a teaching kernel or build an officially documented sample driver in a test VM. Observe load, unload, logging, and failure recovery. Progress to a small real device only after understanding its interface.

Use [Linux kernel documentation](https://www.kernel.org/doc/html/latest/) and [Windows driver documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/). Follow their current toolchain and testing requirements rather than treating old book code as a current installation guide.

### 27.2 Compilers and programming languages

**Prerequisites:** data structures, recursion, trees, parsing, and some assembly/runtime knowledge.

A compiler typically tokenizes text, parses structure, checks meaning, builds an intermediate representation, transforms it, and emits executable code or another target. An interpreter executes the language's meaning through a runtime.

**First project:** implement a calculator with variables, an abstract syntax tree, useful syntax errors, and tests. Add a bytecode VM later. Study scope, types, garbage collection, and optimization after the basic language works.

### 27.3 Distributed systems and backend infrastructure

**Prerequisites:** networking, databases, concurrency, and operations.

Study replication, consensus, leader election, partitions, consistency, clocks, duplicate delivery, and partial failure. A timeout does not tell you whether the remote operation never happened or happened but its response was lost.

**First project:** a durable local job queue with retries and deduplication; then move workers across two processes. Add crash-recovery tests before adding multiple machines. Read [Designing Data-Intensive Applications](https://dataintensive.net/) for deeper architectural reasoning.

### 27.4 DevOps, platform engineering, and SRE

**Prerequisites:** Linux/Windows administration, scripting, networking, CI, deployment, and monitoring.

Learn declarative configuration, infrastructure as code, environment consistency, identity, release strategies, and incident response. Idempotent automation converges toward a desired state rather than accumulating duplicate changes.

**First project:** recreate a practice deployment from documented configuration, then restore its data and measure the recovery. Add Windows and Linux workers if both are relevant to your software.

### 27.5 Security research and reverse engineering

**Prerequisites:** C, assembly basics, OS internals, networking, and debugging.

Learn executable formats such as PE/ELF, disassembly, calling conventions, memory corruption, binary analysis, and secure design. Study legal permissions and project scope before analyzing third-party systems.

**First project:** compile your own small program with and without optimization, inspect its symbols and disassembly, and explain how source constructs changed. Then analyze an intentionally vulnerable local training program and implement a fix.

### 27.6 Embedded systems and IoT

**Prerequisites:** C/C++, binary arithmetic, basic electronics, and serial communication.

Learn GPIO, interrupts, timers, UART, SPI, I2C, memory limits, power constraints, and firmware updates. Bare-metal firmware may lack ordinary OS facilities. An RTOS adds scheduling and synchronization, but deadlines still require careful design.

**First project:** read a harmless sensor, timestamp readings, transmit them to a local application, and handle disconnected hardware. Use appropriate voltage levels and a supported board tutorial.

### 27.7 Graphics, games, and simulation

**Prerequisites:** C++ or another engine language, vectors, matrices, coordinate systems, timing, and profiling.

Learn the update/render loop, input, transformations, collision, assets, shaders, lighting, and resource lifetime. Separate frame rate from simulation step size so behavior does not unintentionally change across machines.

**First project:** a small 2D game with movement, collision, pause, save/load, and packaged builds. Learn engine tooling before attempting a large custom engine. Rendering API selection depends on target platforms and hardware.

### 27.8 Data engineering and analytics

**Prerequisites:** Python, SQL, data modeling, statistics, and testing.

Learn ingestion, schemas, missing values, units, provenance, transformations, orchestration, and reproducibility. Data quality rules should distinguish impossible values from merely unusual ones.

**First project:** import fictional CSV data into a database, validate it, preserve source lineage, and produce a repeatable report. Make reruns avoid duplicate records.

### 27.9 Machine learning and AI applications

**Prerequisites:** Python, linear algebra, probability, data handling, and evaluation.

Learn train/validation/test separation, leakage, baselines, metrics, inference, monitoring, and deployment. For language-model applications, learn retrieval, tool permissions, prompt injection boundaries, evaluation sets, and cost/latency measurement.

**First project:** compare a simple non-ML baseline against a small model on a fixed public or invented dataset. For retrieval, test whether the correct evidence is retrieved before evaluating generated wording.

AI output is not automatically correct code or evidence. Keep a reproducible evaluation rather than relying on a persuasive demonstration.

### 27.10 Mobile applications

**Prerequisites:** programming, UI design, asynchronous work, networking, and storage.

Learn application lifecycle, background-execution limits, permissions, offline behavior, responsive layouts, and signing/distribution. Android development can be practiced from Windows/Linux; Apple-platform build and distribution workflows require their supported tooling and environment.

**First project:** a notes app that works offline and synchronizes changes through an API you control. Define conflict resolution before implementing synchronization.

### 27.11 Scientific and high-performance computing

**Prerequisites:** numerical methods, linear algebra, profiling, and reproducibility.

Learn vectorization, numerical stability, cache locality, parallel decomposition, GPU execution, and distributed computation where necessary. Faster code that changes the scientific meaning is not an improvement.

**First project:** implement a small simulation, validate against a known result, profile it, and compare an optimized implementation within an explicit numerical tolerance.

### 27.12 Enterprise administration and identity

**Prerequisites:** networking, permissions, scripting, and service operations.

Learn directory services, centralized identity, policy, certificate management, inventory, patching, and delegated administration. Local administrator privileges and organization-wide identity authority are different scopes.

**First project:** produce a read-only inventory of your lab machines and a reproducible report. Practice identity and policy changes in an isolated test environment before production use.

### 27.13 Developer tools, build engineering, and open source

**Prerequisites:** Git, testing, packaging, compilers/runtimes, and documentation.

Learn language servers, editor integrations, static analysis, dependency graphs, incremental builds, release automation, and public issue handling.

**First project:** write a project scaffolder or linter with clear errors and tests. Then contribute a small documentation fix or bug reproduction to an existing project, following its contribution rules and licensing requirements.

## 28. Projects with acceptance criteria

These projects turn reading into independent capability. Start with the specified scope, release a working version, then choose extensions. Do not add every optional feature before finishing the core.

### Project A — Cross-platform file and log toolkit

**Prerequisites:** chapters 2–9.  
**Core:** File Summary, text search, JSON/CSV export, and clear errors.  
**Skills:** paths, command-line arguments, encoding, streams, tests, Git.

Acceptance criteria:

- Runs on native Windows and Linux from documented setup instructions.
- Handles empty folders, missing paths, spaces, and non-ASCII names.
- Defines symbolic-link and partial-failure behavior.
- Sends data to standard output and errors to standard error.
- Returns meaningful exit statuses.
- Includes automated tests and sample invented input.

**Stretch:** hashing, duplicate candidates, recursive scanning, progress, and cancellation. Treat matching hashes as part of a defined duplicate-detection strategy; never automatically delete files in the first version.

### Project B — Local task database

**Prerequisites:** Python or C#, SQL, Git, and tests.  
**Core:** add, list, complete, and search tasks with SQLite persistence.

Acceptance criteria:

- State survives process restart.
- Invalid tasks cannot enter through either CLI or storage code.
- Queries use parameters.
- A schema migration is versioned and tested.
- Export and restore work in a new folder.
- A README explains storage location and limitations.

**Stretch:** tags, full-text search, optimistic edit versions, and a desktop UI.

### Project C — Networked task application

**Prerequisites:** project B plus HTTP, backend development, and security foundations.  
**Core:** browser UI, API, database, and per-user task ownership.

Acceptance criteria:

- One user cannot read or modify another user's tasks.
- The server validates requests independently of the browser.
- Authentication uses maintained framework facilities.
- Tests cover malformed requests, denied access, and database failures.
- Configuration and secrets are separate from source code.
- A local deployment, migration, and backup/restore procedure is documented.

**Stretch:** pagination, background jobs, accessibility testing, and a staged hosted deployment.

### Project D — Background indexing service

**Prerequisites:** systems concepts, concurrency, persistence, and operations.  
**Core:** scan approved practice folders and maintain searchable metadata.

Acceptance criteria:

- Works in the foreground before installation as a service.
- Has bounded work queues and graceful cancellation.
- Can resume after interruption without corrupting its index.
- Defines behavior for renamed, removed, inaccessible, and changing files.
- Has Linux and Windows service adapters or explicitly scoped platform support.
- Includes logs, resource limits, an uninstall procedure, and recovery instructions.

**Stretch:** filesystem notifications, periodic reconciliation, and performance profiling. Watch notifications can be missed; design reconciliation rather than treating notifications as a perfect historical record.

### Project E — Native application

**Prerequisites:** C++/Rust/C#, UI basics, native build tools, and packaging.  
**Core:** a responsive desktop frontend for one earlier project.

Acceptance criteria:

- Long tasks do not freeze the window.
- Cancellation and unsaved changes have defined behavior.
- Keyboard navigation and accessible names work.
- Build and install instructions work on a clean supported environment.
- User data survives upgrades.
- At least one real crash or error report has been investigated and documented.

### Project F — One specialization capstone

Choose a compiler, teaching-kernel extension, framed socket service, embedded sensor client, small game, data pipeline, or distributed worker system.

Acceptance criteria:

- States prerequisites and scope.
- Includes an original design decision with alternatives considered.
- Contains a measurable correctness or performance goal.
- Tests failure paths as well as success.
- Produces a usable release or reproducible experiment.
- Includes a postmortem describing what failed and what you learned.

### The independent-build exam

Choose a fresh problem, allow documentation, and avoid copying a complete tutorial implementation. Work from a one-page specification. Deliver source, tests, README, a release artifact where applicable, and a short demonstration of failure recovery.

You pass when you can explain the design, make a new change yourself, and diagnose a deliberately introduced failure. Looking up syntax is allowed; understanding the program is required.

## 29. Study schedule and mastery checkpoints

### 29.1 Planning estimate

At roughly 8–12 focused hours per week, a 9–12 month plan can organize your path toward independent small/medium projects. This is a suggested schedule, not a promise of mastery; prior experience, project scope, and deliberate practice change the pace. Deep systems specialization generally takes repeated projects beyond this foundation.

### 29.2 Suggested sequence

- **Weeks 1–2:** computer basics, lab setup, paths, and basic commands.
- **Weeks 3–6:** Bash, PowerShell, Python fundamentals, and Git.
- **Weeks 7–10:** project A, tests, debugging, and a clean-machine run.
- **Weeks 11–14:** algorithms, C, memory, and build tools.
- **Weeks 15–18:** OS concepts, Linux/Windows observation, and networking.
- **Weeks 19–22:** databases and project B.
- **Weeks 23–28:** web/API or desktop track; begin project C or E.
- **Weeks 29–34:** security, packaging, CI, containers, and recovery.
- **Weeks 35–40:** project D or a second substantial independent project.
- **Weeks 41–52:** one specialization, capstone, and portfolio refinement.

If time is limited, finish A and B before learning a second compiled language. If Windows desktop work is your main aim, emphasize C# and native Windows tools. If Linux infrastructure is your aim, emphasize Bash, networking, services, and deployment. If kernels are your aim, extend C, architecture, and OS study before drivers.

### 29.3 Weekly routine

For a ten-hour week: two hours of focused reading, five hours building, two hours debugging/testing, and one hour reviewing and documenting. Once every few weeks, recreate a small feature without the original instructions.

Use a progress scale for each topic:

- **0:** unfamiliar.
- **1:** can explain the idea.
- **2:** can complete a guided exercise.
- **3:** can implement independently with documentation.
- **4:** can diagnose failures and explain tradeoffs.

Mark progress based on demonstrated work. Finishing a video does not automatically advance a score.

### 29.4 Gates

- [ ] **Foundation gate:** navigate both OSes, run a script, and explain paths/permissions.
- [ ] **Programming gate:** implement a utility and test it without a tutorial.
- [ ] **Systems gate:** explain process/memory/I/O behavior and investigate a failure.
- [ ] **Data gate:** design a schema, migrate it, and restore it.
- [ ] **Application gate:** build a useful CLI, UI, or API with clear boundaries.
- [ ] **Release gate:** build from a clean checkout and preserve data through upgrade.
- [ ] **Independence gate:** complete the independent-build exam.

## 30. Books, courses, and documentation

Choose **one main book/course at a time**, plus official documentation for your current tools. You do not need to purchase the entire list. Several authors and universities provide legal free material; a printed edition is optional. Recommendation fit and reading order below are editorial guidance.

### 30.1 Start with these

1. **The Linux Command Line — William Shotts.** Beginner shell foundation; read alongside chapters 4–5 and do the exercises. The [author's site](https://linuxcommand.org/tlcl.php) provides legal learning editions; [No Starch Press](https://nostarch.com/node/820) lists the third print edition. Online and print editions can differ.
2. **Automate the Boring Stuff with Python — Al Sweigart.** Beginner programming through practical tasks. Use it while building project A; its [author-hosted text](https://automatetheboringstuff.com/) is free to read.
3. **Pro Git — Scott Chacon and Ben Straub.** Learn the repository model, branching, and collaboration. The [official book site](https://git-scm.com/book/en/v2) provides the text free online.
4. **Microsoft Learn PowerShell documentation.** Follow [the PowerShell overview and linked learning paths](https://learn.microsoft.com/en-us/powershell/scripting/overview), reproducing equivalent Bash and PowerShell tasks. Focus on objects and error handling, not memorized aliases.
5. **CS50x — Harvard.** A structured computer-science foundation for beginners. Work through actual problem sets using the [official course](https://cs50.harvard.edu/x/); free OpenCourseWare and paid credential options are distinct.

**Minimal starting selection:** one beginner programming resource, *The Linux Command Line*, PowerShell documentation, and *Pro Git*. Start project A immediately alongside them.

### 30.2 Core systems books

6. **Operating Systems: Three Easy Pieces — Remzi H. Arpaci-Dusseau and Andrea C. Arpaci-Dusseau.** Read after basic C. Focus on processes, memory, concurrency, and persistence. [Free chapters and exercises](https://pages.cs.wisc.edu/~remzi/OSTEP/) are hosted by the authors' university.
7. **The Linux Programming Interface — Michael Kerrisk.** A substantial Linux/Unix system-programming reference. Use after C and basic OS concepts; implement small API experiments while reading. See [the author's site](https://man7.org/tlpi/). Pair it with current manual pages for evolving interfaces.
8. **Windows Internals — the series linked by Microsoft Sysinternals.** Advanced reading for processes, memory, security, and Windows architecture. Choose the relevant part/edition through [Microsoft's book page](https://learn.microsoft.com/en-us/sysinternals/resources/windows-internals); do not use older version-specific details as current API guarantees.
9. **Beej's Guide to Network Programming — Brian “Beej Jorgensen” Hall.** Practical socket concepts after C and networking basics. [Free online guide](https://beej.us/guide/bgnet/). Follow its platform notes when adapting examples to Windows.
10. **Systems Performance, second edition — Brendan Gregg.** Advanced measurement and diagnosis after you can build and operate a service. [Author's resource page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html).

### 30.3 Languages and application development

- **Python:** [official tutorial](https://docs.python.org/3/tutorial/); use it as a language reference after initial beginner practice.
- **Rust:** [The Rust Programming Language](https://doc.rust-lang.org/book/); read with small Cargo projects and tests.
- **C#/.NET:** [Microsoft's console tutorial](https://learn.microsoft.com/en-us/dotnet/core/tutorials/create-console-app?pivots=vscode); continue through language, testing, and publishing documentation.
- **Windows desktop:** [choose a Windows development path](https://learn.microsoft.com/en-us/windows/apps/get-started/), then follow the chosen framework's maintained tutorial.
- **Web:** [MDN Learn Web Development](https://developer.mozilla.org/en-US/docs/Learn_web_development); use for HTML, CSS, JavaScript, and accessible browser behavior.
- **SQL:** [PostgreSQL's tutorial](https://www.postgresql.org/docs/current/tutorial.html); practice queries and relationships rather than only using an ORM.
- **Build tooling:** [CMake documentation](https://cmake.org/documentation/); progress from one executable to libraries, tests, and installation rules.

### 30.4 Courses and deeper routes

- **The Missing Semester of Your CS Education — MIT:** [course site](https://missing.csail.mit.edu/). Use for shell, tools, debugging, and efficient workflows after basic command-line familiarity.
- **Introduction to Linux, LFS101 — Linux Foundation:** [course page](https://training.linuxfoundation.org/training/introduction-to-linux/). A free introductory course; useful if you prefer a structured Linux learning sequence.
- **Nand2Tetris:** [official course and book resources](https://www.nand2tetris.org/). Build understanding from logic gates toward a software stack; take it as a focused architecture course rather than a prerequisite to every app.
- **Designing Data-Intensive Applications:** [official book site](https://dataintensive.net/). Read after building a database-backed service. Choose an edition deliberately using the current site; use the book to reason about tradeoffs, not as a recipe for adding distributed components to every project.
- **OWASP Cheat Sheet Series:** [project site](https://owasp.org/www-project-cheat-sheets/). Consult the relevant sheet while implementing a security-sensitive feature.
- **Linux kernel documentation:** [official documentation](https://www.kernel.org/doc/html/latest/). Specialist route after C, concurrency, and OS foundations.
- **Windows drivers:** [Microsoft documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/). Specialist route with the current supported toolchain and test environment.

### 30.5 How to use a book well

For each chapter, write a short explanation without looking, implement one exercise, create one failure, and connect the mechanism to your project. Keep a list of unanswered questions. Skip ahead only when you can demonstrate the chapter's key skill or it is outside your selected route.

Do not buy a new resource just because the current subject becomes difficult. First reduce the exercise, inspect the failure, and ask a focused question. Prefer resources with runnable exercises, clear prerequisites, maintained errata, and primary documentation links.

## 31. Troubleshooting playbook

### “Command not found” or “not recognized”

Check the shell, spelling, installation, executable location, and `PATH`. Use `command -v` in Bash or `Get-Command` in PowerShell. A tool installed inside WSL is not automatically installed natively in Windows. A compiler may require its developer shell.

### “It works in my terminal but not in my editor”

Compare interpreter path, environment variables, working directory, arguments, and user identity. Editors may retain an environment from before installation or choose a different virtual environment.

### “Permission denied” or “access denied”

Inspect the exact path and process identity. Check parent-directory access, file ACLs/modes, read-only state, file sharing, and platform security policies. Fix the smallest correct permission or location issue rather than broadly elevating the program.

### “Module or DLL not found”

Separate language package discovery from native library loading. Verify the active environment, architecture, runtime dependencies, and search paths. A Python package may import successfully on one platform but depend on a missing native library on another.

### “Address already in use”

Inspect which process owns the intended listening port. Confirm it is your previous server before stopping it. Alternatively choose another documented port and update the client configuration.

### “The program hangs”

Determine whether it is computing, waiting for input, blocked on I/O, waiting for a lock, or stuck in a loop. Use a debugger and process metrics. Add a timeout at the correct boundary; repeatedly increasing timeouts can hide a deadlock.

### “The data disappeared”

Check the absolute database/file location, working directory, environment, container volume, and whether the database was in memory. Verify the application did not silently create a new empty database elsewhere.

### “Tests pass, users still see a bug”

Compare the tested assumptions with real inputs, concurrency, permissions, and configuration. Reproduce the user's path in a controlled environment. Add a regression test at the layer where the original suite had a gap.

### “It works on Windows but fails on Linux”

Check filename case, separators, line endings, execute bits, unavailable binaries, hardcoded drive letters, native dependencies, and shell assumptions. Reverse the investigation for Linux-to-Windows failures, adding ACLs and open-file behavior.

### “It is slow”

Measure the exact operation and input. Check CPU, memory pressure, I/O waits, repeated network calls, database query count, and algorithmic growth. Keep a benchmark so you can tell whether the proposed fix actually helps.

## 32. Glossary and independent-build checklist

### Essential glossary

- **ABI:** binary-level agreement about calling functions and laying out data.
- **API:** interface that software exposes to other software.
- **Artifact:** a produced output such as an executable, package, or report.
- **Atomicity:** an operation's specified all-or-nothing or indivisible behavior; scope matters.
- **CLI:** command-line interface.
- **Dependency:** external code, tool, or service your software relies on.
- **Deterministic:** same defined inputs/state produce the same result.
- **Idempotent:** repeating the same operation has the same intended effect as applying it once.
- **IPC:** inter-process communication.
- **Latency:** time taken for an operation or response.
- **Library:** reusable code used by a program.
- **Lock:** synchronization mechanism controlling access to shared state.
- **Migration:** versioned change to stored data or schema.
- **Package manager:** tool for obtaining and managing software packages.
- **Protocol:** rules for communication.
- **Runtime:** execution support required by a program.
- **SDK:** development tools and libraries for a platform or system.
- **Serialization:** converting structured values to a storable/transmittable representation.
- **Throughput:** amount of work completed per unit of time.
- **Transaction:** group of database operations governed by stated consistency/commit rules.
- **Undefined behavior:** behavior for which a language specification imposes no requirements in the given circumstances.

### Before calling a project complete

- [ ] I can state the problem and intended user.
- [ ] I can explain every major module and dependency.
- [ ] Inputs, outputs, and errors have documented contracts.
- [ ] Important rules and failure paths have meaningful tests.
- [ ] I have run it from a clean setup on every claimed platform.
- [ ] Configuration and user data have deliberate locations.
- [ ] Secrets are absent from source, logs, and release artifacts.
- [ ] Access controls are enforced where authority actually resides.
- [ ] Installation and upgrade instructions are reproducible.
- [ ] A backup has been restored successfully where persistence matters.
- [ ] Known limitations are honest and visible.
- [ ] I can implement a new requirement without rebuilding from a tutorial.

### Working with AI while retaining independence

Ask for an explanation, a small example, or a review of your reasoning. Predict what generated code will do before running it. Check documentation for unfamiliar APIs. Add a test based on the requirement rather than trusting a test that merely repeats the implementation.

Regularly build a small feature without generated code, then use assistance to review it. Never equate plausible wording with verified correctness. Your aim is to make informed decisions, investigate failures, and understand the system you ship.

## 33. Validation and limitations

This handbook is educational material, not a record of an installed development environment or a completed training program. Setup commands, service exercises, native builds, browser examples, and deployment instructions require verification in your selected lab.

The first CLI and its tests are self-contained standard-library Python examples. The SQLite example uses an in-memory database and invented data. No real application databases or user research files are needed for these exercises.

### Checks completed on 15 September 2026

- All 33 internal contents links resolved to headings, and all 37 fenced code blocks were balanced.
- All four Python code blocks parsed successfully.
- All three File Summary unit tests passed on Windows using the existing project Python environment.
- Additional CLI checks verified expected JSON for a folder with spaces in its path, and exit status 1 with a diagnostic on standard error for a missing directory.
- The SQLite example ran and produced the documented result.
- The C example compiled without warnings using the installed Windows MinGW GCC with C17 and the documented GCC warning flags, and printed `60`.
- All 12 PowerShell blocks passed syntax parsing with the available Windows PowerShell parser. Parsing does not establish successful execution or installed prerequisites.
- Verification used temporary invented files that were removed afterward. It did not run the existing application's test suite or alter its dependencies.

### Not verified here

Linux execution, Bash scripts, native MSVC compilation, CMake builds, .NET commands, browser rendering, service installation, container/cloud deployment, UI accessibility, and clean-machine packaging were not executed. The examples and exercises in those areas require their stated prerequisites and lab validation. The CMake documentation site timed out or returned retrieval errors during source checking; its link is supplied as the official reference, not as a successfully inspected page.

Further claims of cross-platform support should be based on actual Windows and Linux execution, not inferred solely from portable-looking source. The study schedule is a planning aid, and the specialist chapters are entry routes to deeper study rather than exhaustive references.
