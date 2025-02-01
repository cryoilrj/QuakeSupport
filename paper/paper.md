---
title: 'QuakeSupport: Streamlining end-to-end QuakeMigrate processing with GrowClust integration'
tags:
  - Python
  - Fortran
  - seismology
  - geophysics
  - QuakeMigrate
  - GrowClust
  - QuakeSupport
  - seismic data processing
  - data downloader
  - automated workflows
authors:
  - name: Ian R.J. Lee
    orcid: 0000-0001-6871-266X
    corresponding: true
    affiliation: 1
  - name: Richard B. Alley
    orcid: 0000-0003-1833-0115
    affiliation: 1
  - name: Sridhar Anandakrishnan
    orcid: 0000-0001-8229-2593
    affiliation: 1
affiliations:
 - name: Department of Geosciences, Pennsylvania State University, University Park, PA, USA
   index: 1
date: 31 January 2025
bibliography: paper.bib
---

# Summary

QuakeMigrate and GrowClust are powerful seismic processing tools that naturally complement each other—QuakeMigrate detects and locates events, while GrowClust relocates them with greater precision, leveraging QuakeMigrate's robust event locations and picks. However, users face three key challenges: manual input data preparation and formatting, efficiently managing extended QuakeMigrate runs, and the lack of built-in support for exporting QuakeMigrate outputs to GrowClust. `QuakeSupport` addresses these challenges by automating the end-to-end QuakeMigrate workflow with partitioned runs and enabling integration with GrowClust.

# Statement of need

`QuakeSupport` is a Python script suite that facilitates a seamless processing pipeline between QuakeMigrate and GrowClust while improving performance, particularly for extended QuakeMigrate runs. QuakeMigrate [@Winder:2022] is a Python-based software that automates the detection and location of earthquakes through the use of waveform migration and stacking methods. GrowClust [@Trugman:2017] is a Fortran-based software for earthquake hypocenter relocation using differential times derived from waveform cross-correlation data.

QuakeMigrate and GrowClust are highly effective for generating high-granularity seismic event catalogs, but users face several challenges. Input data preparation and formatting require significant manual effort, which becomes increasingly time-consuming and labor-intensive when performed across multiple seismic arrays, time periods, and large MiniSEED (mSEED) datasets. Additionally, during QuakeMigrate's detect and locate stages, seismic data read times can become prohibitively long with large files, even when only a small subset of the data is used. Reducing the time window per run and limiting input data size can mitigate long read times in QuakeMigrate, but managing and partitioning runs still demand considerable manual effort and introduce additional oversight. QuakeMigrate also currently does not have built-in support for exporting outputs to GrowClust, requiring users to manually convert the data.

`QuakeSupport` addresses these challenges through four core capabilities:

+ A seamless processing pipeline (\autoref{fig:QS_wf}) that automates seismic data download and preparation, partitioning and execution of QuakeMigrate runs, and conversion of QuakeMigrate outputs into GrowClust-compatible inputs, effectively bridging the gap between QuakeMigrate and GrowClust.
+ Automates input data preparation and formatting for both QuakeMigrate and GrowClust, ensuring workflow compatibility.
+ Automates management and partitioning of QuakeMigrate runs into smaller time chunks, reducing data-reading overhead and improving processing efficiency, particularly for extended time periods, including both continuous and discontinuous intervals.
+ A modular design that includes three scripts capable of functioning independently outside the `QuakeSupport` ecosystem: a multithreaded seismic data downloader for concurrent downloads, a QuakeMigrate modeled and observed picks plotter, and a simple waveform inspection tool.

![`QuakeSupport` workflow, consisting of the QuakeMigrate and GrowClust modules. Arrows indicate the sequence for running the `QuakeSupport` scripts, with optional scripts enclosed in dashed boxes. Users interested in running only QuakeMigrate can omit the GrowClust module.\label{fig:QS_wf}](QS_wf.png)

Beyond managing the complexities and intricacies of data preparation, data and run partitioning, and execution, `QuakeSupport` focuses on accessibility and ease of use. It centralizes user-modifiable parameters in dedicated configuration sections for intuitive access. It also leverages multithreading and multiprocessing for performance, and runs cross-platform on Linux, Windows, and Mac. A test module using 2018-2019 Rutford Ice Stream 5B network data [@Anandakrishnan:2018] is provided for validation and familiarization. A comprehensive user guide details configuration, usage, and best practices.

`QuakeSupport` was developed to ease the learning curve of the QuakeMigrate and GrowClust workflows, drawing on years of hands-on experience with icequake research in Rutford Ice Stream, West Antarctica [@Lee:2020; @Lee:2021; @Lee:2022; @Lee:2023; @Lee:2024; @Lee:2025]. It was conceived in response to challenges and user pain points encountered while using QuakeMigrate and GrowClust. Designed for both experienced seismologists and students, it supports users working with QuakeMigrate and GrowClust together, QuakeMigrate alone, or standard seismology tasks such as efficient data downloading. By combining automation, performance enhancement, and modularity, `QuakeSupport` enables researchers to dedicate more effort to seismic analysis and discovery.

# Future work

`QuakeSupport` is continuously evolving to incorporate new functionality and remain compatible with QuakeMigrate and GrowClust updates. For suggestions and comments, please contact Ian Lee at [ianrj.lee@gmail.com](mailto:ianrj.lee@gmail.com).

# Acknowledgements

We thank Amanda Willet for testing the `QuakeSupport` prototypes and providing valuable feedback that helped identify user pain points and improve functionality. We also extend our gratitude to the developers of QuakeMigrate (particularly Conor Bacon and Tom Winder) and GrowClust (particularly Daniel Trugman) for developing these remarkable and invaluable tools upon which `QuakeSupport` builds, as well as for their readiness to address questions related to their software. Lastly, we thank Pennsylvania State University and the British Antarctic Survey for making the test run dataset available, which was collected with support from the U.S. National Science Foundation (NSF) award 1643961.

# References