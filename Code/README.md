# **BIMERR OBXML CODE**

The [`requirements.txt`](./requirements.txt) file should list all Python libraries that your notebooks
depend on, and they will be installed using:

```
pip install -r requirements.txt
```

Should also install [Java 1.8](https://www.oracle.com/es/java/technologies/javase/javase-jdk8-downloads.html)

## **HOW TO**

- Save idf files into [Examples folder](../Examples)
- Execute the following command:
    ```
    python3 preprocess.py -p ../Examples/in.xml
    ```
- Go to [Execute Mappings folder](../Execute_Mappings)
- Execute the following command:
    ```
    python3 timer.py 
    ```
    This command will execute [Helio](https://oeg-upm.github.io/helio/), that reads the mappings and transform the data to RDF format.
- RDF Files will be saved into [Execute Mappings folder](../Execute_Mappings)