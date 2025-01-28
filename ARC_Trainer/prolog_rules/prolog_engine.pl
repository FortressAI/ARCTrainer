% prolog_engine.pl
% This file loads all domain-specific rules for the ARC Trainer system.

% Debug: Notify when Prolog starts loading rules
:- format("📌 [Prolog] Starting rule loading...\n").

% Load domain-specific rules in order
load_rule(File) :-
    (   consult(File)
    ->  format("✅ [Prolog] Successfully loaded: ~w\n", [File])
    ;   format("❌ [Prolog] Failed to load: ~w\n", [File])
    ).

% Load all rules with debug tracking
:- load_rule('algebra_rules.pl').
:- load_rule('aristotle_logic.pl').
:- load_rule('combinatorics_rules.pl').
:- load_rule('education_rules.pl').
:- load_rule('geometry_rules.pl').
:- load_rule('healthcare_rules.pl').
:- load_rule('legal_rules.pl').
:- load_rule('number_theory_rules.pl').
:- load_rule('warfare_rules.pl').

% Dependency Checker: Ensures that necessary predicates exist before execution
check_dependency(Rule) :-
    (   current_predicate(Rule/_)
    ->  format("✅ [Prolog] Dependency exists: ~w\n", [Rule])
    ;   format("⚠️ [Prolog] Warning: Missing required dependency ~w\n", [Rule])
    ).
