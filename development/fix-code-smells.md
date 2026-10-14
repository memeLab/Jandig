# Fixing code smells on project

To identify and map python code smells on Jandig project, the development team uses [Prospector](https://github.com/PyCQA/prospector). Prospector is a Python tool used to output information about errors, unnecessary code complexity and convention violations for the language.    


## Installation

Before installing Prospector, you need to assure that pip is properly installed on your machine. Once you have pip, you can simply type the command

```
pip install prospector
```

You can also follow the [official Prospector installation guide](https://github.com/PyCQA/prospector#installation).    


## Running Prospector on Jandig

To get the information about code smells you need just to run the following command on the root directory of Jandig:

```
prospector
```

If you want to store the output on a ```.txt``` file, you can must the following command:

```
prospector > filename.txt
```