% combinatorics_rules.pl
% Domain-specific rules for IMO Combinatorics problems
% Now includes human-readable mappings (Controlled Natural Language - CNL)

% --- Debugging & Configuration ---
:- discontiguous cnl_to_prolog/3.
:- discontiguous cnl_to_prolog/4.
:- discontiguous prolog_to_cnl/3.
:- discontiguous prolog_to_cnl/4.
:- multifile cnl_to_prolog/3.
:- multifile prolog_to_cnl/3.

% --- Core Combinatorial Principles ---

% Calculates factorial (n!) recursively.
factorial(0, 1).
factorial(N, F) :-
    N > 0,
    N1 is N - 1,
    factorial(N1, F1),
    F is N * F1.

% Calculates permutations (nPr) - Number of ways to arrange R objects from a set of N.
permutation(N, R, P) :-
    N >= R,
    factorial(N, F1),
    factorial(N - R, F2),
    P is F1 // F2.

% Calculates combinations (nCr) - Number of ways to choose R objects from a set of N.
combination(N, R, C) :-
    N >= R,
    factorial(N, F1),
    factorial(R, F2),
    factorial(N - R, F3),
    C is F1 // (F2 * F3).

% Calculates combinations using the Stars and Bars method.
stars_and_bars(N, K, Result) :-
    N >= 0,
    K > 0,
    combination(N + K - 1, K - 1, Result).

% Applies the Principle of Inclusion-Exclusion for two sets.
inclusion_exclusion(A, B, Intersection, Union) :-
    Union is A + B - Intersection.

% Applies the Principle of Inclusion-Exclusion for three sets.
inclusion_exclusion(A, B, C, AB, AC, BC, ABC, Union) :-
    Union is A + B + C - AB - AC - BC + ABC.

% --- Validation Rules ---

% Validates a combinatorial problem using a language game.
validate_combination_problem(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "validate_combination_problem",
            terms: ["choose", "combination"],
            validation_logic: validate_combination_logic,
            intent_data: IntentData
        }
    ).

% Validates a permutation problem using a language game.
validate_permutation_problem(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "validate_permutation_problem",
            terms: ["arrange", "permutation"],
            validation_logic: validate_permutation_logic,
            intent_data: IntentData
        }
    ).

% --- Combinatorial Learning System ---
% Allows Prolog to store and recall previously solved combinatorial problems.

learn_combination(N, R, C) :-
    assertz(solved_combination(N, R, C)),
    format("Combination learned: C(~w, ~w) = ~w.", [N, R, C]).

recall_combination(N, R, C) :-
    solved_combination(N, R, C),
    format("Previously solved: C(~w, ~w) = ~w.", [N, R, C]).

learn_permutation(N, R, P) :-
    assertz(solved_permutation(N, R, P)),
    format("Permutation learned: P(~w, ~w) = ~w.", [N, R, P]).

recall_permutation(N, R, P) :-
    solved_permutation(N, R, P),
    format("Previously solved: P(~w, ~w) = ~w.", [N, R, P]).

% --- Combinatorial Query Handling ---

% Extracts numbers for combinatorial problems.
extract_numbers_from_statement(Statement, [_N, _R]) :-  % `_N, _R` now marked as unused
    % Simulated logic to extract numbers from input.
    % Replace with actual number extraction methods or NLP-based parsing.
    atom_chars(Statement, Chars),
    findall(_Number, (member(Char, Chars), atom_number(Char, _Number)), _Numbers).

% Validates the result in the original statement.
validate_result_in_statement(Statement, Result) :-
    atom_number(ResultStr, Result),
    play_language_game(
        Statement,
        game_data{
            type: "validate_result",
            result: ResultStr
        }
    ).

% --- Controlled Natural Language (CNL) Mappings ---

% Converts a human-readable statement into a Prolog rule.
cnl_to_prolog("The number of ways to arrange R objects from a set of N objects is given by permutations.", 
              permutation(N, R, P) :- N >= R, factorial(N, F1), factorial(N - R, F2), P is F1 // F2).

cnl_to_prolog("The number of ways to choose R objects from a set of N objects is given by combinations.", 
              combination(N, R, C) :- N >= R, factorial(N, F1), factorial(R, F2), factorial(N - R, F3), C is F1 // (F2 * F3)).

cnl_to_prolog("The inclusion-exclusion principle for two sets states that the union of A and B is given by A + B minus their intersection.", 
              inclusion_exclusion(A, B, Intersection, Union) :- Union is A + B - Intersection).

% Converts a Prolog rule into a human-readable statement.
prolog_to_cnl(permutation(N, R, P) :- N >= R, factorial(N, F1), factorial(N - R, F2), P is F1 // F2, 
              "The number of ways to arrange R objects from a set of N objects is given by permutations.").

prolog_to_cnl(combination(N, R, C) :- N >= R, factorial(N, F1), factorial(R, F2), factorial(N - R, F3), C is F1 // (F2 * F3), 
              "The number of ways to choose R objects from a set of N objects is given by combinations.").

prolog_to_cnl(inclusion_exclusion(A, B, Intersection, Union) :- Union is A + B - Intersection, 
              "The inclusion-exclusion principle for two sets states that the union of A and B is given by A + B minus their intersection.").

% --- Example Usage ---

% learn_combination(10, 2, 45).
% recall_combination(10, 2, C). -> Previously solved: C(10, 2) = 45.
% learn_permutation(5, 3, 60).
% recall_permutation(5, 3, P). -> Previously solved: P(5, 3) = 60.
% validate_combination_problem("There are 45 ways to choose 2 elements from a set of 10.", intent_data{primary_intent: solve_problem}).
% validate_permutation_problem("The number of permutations of 5 objects taken 3 at a time is 60.", intent_data{primary_intent: solve_problem}).
