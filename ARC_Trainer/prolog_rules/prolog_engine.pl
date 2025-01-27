% prolog_engine.pl

% This file is used to load all the necessary prolog rules for the ARC Trainer system.

% Load domain-specific rules
consult('algebra_rules.pl').
consult('aristotle_logic.pl').
consult('combinatorics_rules.pl').
consult('education_rules.pl').
consult('geometry_rules.pl').
consult('healthcare_rules.pl').
consult('legal_rules.pl').
consult('number_theory_rules.pl').
consult('warfare_rules.pl').

% You can add more consult statements here for additional .pl files

% You can also add rules directly to this file if you want

% Example of a rule
% example_rule(X) :- write('This is an example rule: '), write(X).
