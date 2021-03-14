## A semi-random collection of Python bits and pieces
Most everything expects a logger named `logger`.

### \_\_init.py\_\_ 
```get_abs_path``` -> Get the absolute path to the module

### Utils 
```setup_logging``` -> Logger setup

```format_bytes``` -> Convert bytes to human-readable strings

```exiter``` -> Generic app exiter

```image_format_converter``` -> Use Pillow to convert images between formats

```signal_handler``` -> Catch signal interrupts

```get_platform``` -> Return the platform we're running on

```aggregate_list_dupes``` -> Return a dict with frequency count of elements in a given list

```check_root``` -> Platform independent checker for root/admin permissions. 

```enumerate_sub_dirs``` -> Returns a list of all directories below `root_dir`.

```diff_lists``` -> Returns a list of items in `list_a` that are not in `list_b`.

```y_n``` -> Process the result of a Yes/No prompt.

```merge_dicts``` -> Merges `dict_b` into `dict_a`.

### DateTimeFormatter
One place to format timestamps for human consumption.

### DoHttp
My generic Requests wrapper.

### INIConfiguration
My generic ConfigParser wrapper that converts ConfigParser <--> dict.

### PathDetails
One place to manage paths.

### ServiceCreator
Service creators/managers for SystemD, macOS, Windows.

### SubProcessor
My generic Subprocess wrapper.