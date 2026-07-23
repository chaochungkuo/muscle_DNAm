# Data interface

Data are not included in this repository. The public datasets used in this research are GSE315831 and GSE121961.

Configure external paths in `config/paths.local.yml`, copied from `config/paths.example.yml`. Never commit IDAT files, complete M/B-value matrices, external cohort data, or fitted models.

The rebuilt workflow validates inputs using dimensions, explicit sample identifiers, and checksums before analysis.
