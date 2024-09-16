# `multifunctional` Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.2] - 2024-09-16

Add `check_property_for_process_allocation` function

## [0.7.1] - 2024-09-04

* Packaging fix

## [0.7] - 2024-09-04

* [# 21: Add custom allocation functions and validation](https://github.com/brightway-lca/multifunctional/pull/21)

## [0.6] - 2024-08-21

* Fix [#19: Store default allocation value and function string on mutifunctional processes](https://github.com/brightway-lca/multifunctional/issues/19)
* Fix [#18: Allocation functions should primarily get properties from nodes, not exchanges](https://github.com/brightway-lca/multifunctional/issues/18)
* Fix `bw2data` [#182: `multifunctional` import doesn't add new process types to `labels.node_types`](https://github.com/brightway-lca/brightway2-data/issues/182)

### [0.5.1] - 2024-07-19

* Add codes to functional exchanges with zero allocation factors in multifunctional processes

### [0.5] - 2024-07-08

* Allow products to overwrite process names when importing SimaPro

### [0.4.3] - 2024-07-08

* Remove unneeded dependency on `bw_simapro_csv`

### [0.4.2] - 2024-07-08

* Change "manual" allocation and property key to "manual_allocation".

### [0.4.1] - 2024-07-07

* Add capability for property-based allocation  to not be normalized by production amount
* Manual property-based allocation is not normalized by production amount

### [0.4.0] - 2024-07-07

* Collapse `MaybeMultifunctionalProcess` and `MultifunctionalProcess`
* Suppress logs to STDOUT by default

## [0.3.0] - 2024-07-06

* Rewrite allocation functionality to allow for allocation before writing the database

## [0.2.0] - 2024-07-05

* Allow separate products and processes
* Allow specifying desired codes for allocated processes
* Mark strategy functions used for allocation

## [0.1.0] - 2024-07-04

First complete release

### Added

### Changed

### Removed
