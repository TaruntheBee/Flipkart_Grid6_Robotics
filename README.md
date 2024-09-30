# Flipkart Grid 6 Robotics

This project is part of the Flipkart Grid 6 Robotics competition. 
Objective: Design a smart quality test system utilizing camera vision technology for India’s 
leading ecommerce company. The system should be able to assess the shipment quality 
and quantity effectively and efficiently.
## Table of Contents
- [Cloning the Repository](#cloning-the-repository)
- [Setup](#setup)
  - [Creating a Virtual Environment](#creating-a-virtual-environment)
  - [Installing Requirements](#installing-requirements)
- [How to Run the Project](#how-to-run-the-project)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## Cloning the Repository

To get started with the project, clone the repository using the following command:

```bash
git clone https://github.com/TaruntheBee/Flipkart_Grid6_Robotics.git
```
Then, navigate to the project directory:

```bash
cd Flipkart_Grid6_Robotics
```
## Setup

Follow the steps below to set up the project on your local machine.

### Creating a Virtual Environment

1. Open your terminal/command prompt.

2. Navigate to the project directory.

3. Run the following command to create a virtual environment. Replace `myenv` with your preferred environment name:

    ```bash
    python -m venv myenv
    ```

4. Activate the virtual environment:

    - On **Windows**:
      ```bash
      .\venv_name\Scripts\activate
      ```

    - On **macOS/Linux**:
      ```bash
      source venv_name/bin/activate
      ```

### Installing Requirements

Once the virtual environment is activated, install the necessary dependencies from the `requirements.text` file:

```bash
pip install -r requirements.txt
```

### How to Run the Project

After setting up the virtual environment and installing the dependencies, ensure that your Arduino is properly connected. Run the main script:
```bash
python main.py
```
