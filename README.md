# Minimizing Mismatch Loss with Genetic Algorithms

Welcome to the **Final Thesis Project**, where we employ **Genetic Algorithms** to generate optimal configurations of solar panels, minimizing mismatch loss and improving overall energy efficiency.

## 🚀 Quick Start

To get started, make sure you have the latest version of Python installed (minimum version required: **3.12.5**).

### 1. Clone the Repository

git clone

### 2. Add Your Dataset
Place your `.csv` entry file in the cloned project and name it **`dataset.csv`**. Alternatively, you can update the file path directly in the code:
- **Edit line 13** of `main.py` to point to your dataset.

### 3. Customize Parameters
Within the **`main.py`** file, edit the parameters between **lines 22 and 29** to match your project’s settings:
- Population size
- Number of generations
- Mutation rate
- Characteristics of solar panels (C, L, M, N values)

### 4. Run the Program
Navigate to the `src` folder and execute the script:

python main.py


## 🛠 Project Overview
This project is designed to optimize solar panel configurations using **genetic algorithms**, reducing energy loss due to mismatched solar panel characteristics.

- **Genetic Algorithms**: Used to search for the best configuration that minimizes mismatch loss.
- **Custom Parameters**: Adaptable to your solar panel setup for optimal results.
- **CSV Dataset**: Your input data should reflect real-world solar panel specifications for accurate performance.

## 📄 Requirements
- **Python**: 3.12.5 or later
- **Libraries**: Listed in `requirements.txt` (install with `pip install -r requirements.txt`)

## 📧 Need Help?
If you encounter any issues or have questions about setting up or customizing the project, feel free to open an issue or reach out.

---

*Happy optimizing! 🌞*
