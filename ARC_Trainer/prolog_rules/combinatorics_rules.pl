% Domain-specific rules for IMO Combinatorics problems
% Now includes human-readable mappings (Controlled Natural Language - CNL)

% --- Core Combinatorial Principles ---

% Calculates factorial (n!) recursively.
factorial(0, 1).
factorial(N, F) :-
    N > 0,
    N1 is N - 1,
    factorial(N1, F1),
    F is N * F1.

% Calculates permutations (nPr).
permutation(N, R, P) :-
    N >= R,
    factorial(N, F1),
    factorial(N - R, F2),
    P is F1 // F2.

% Calculates combinations (nCr).
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
validate_statement(Statement, IntentData) :-
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
validate_permutation_statement(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "validate_permutation_problem",
            terms: ["arrange", "permutation"],
            validation_logic: validate_permutation_logic,
            intent_data: IntentData
        }
    ).

% --- Combinatorial Language Game Logic ---

% Logic for validating a combination statement.
validate_combination_logic(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: solve_problem},
    parse_combinatorial_statement(Statement, N, R),
    combination(N, R, Result),
    validate_result_in_statement(Statement, Result).

% Logic for validating a permutation statement.
validate_permutation_logic(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: solve_problem},
    parse_combinatorial_statement(Statement, N, R),
    permutation(N, R, Result),
    validate_result_in_statement(Statement, Result).

% --- Parsing Logic ---

% Parses a combinatorial problem statement.
parse_combinatorial_statement(Statement, N, R) :-
    play_language_game(
        Statement,
        game_data{
            type: "parse_statement",
            parsing_logic: extract_numbers,
            result_vars: [N, R]
        }
    ).

% Extracts numbers for combinatorial problems.
extract_numbers(Statement, [N, R]) :-
    % Example logic for extracting numbers (simulated).
    % Replace with proper number extraction logic.
    sub_string(Statement, _, _, _, "choose"),
    sub_string(Statement, _, _, _, NStr),
    sub_string(Statement, _, _, _, RStr),
    atom_number(NStr, N),
    atom_number(RStr, R).

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
cnl_to_prolog("The number of ways to arrange R objects from a set of N objects is given by permutations.", permutation(N, R, P) :- N >= R, factorial(N, F1), factorial(N - R, F2), P is F1 // F2).

cnl_to_prolog("The number of ways to choose R objects from a set of N objects is given by combinations.", combination(N, R, C) :- N >= R, factorial(N, F1), factorial(R, F2), factorial(N - R, F3), C is F1 // (F2 * F3)).

cnl_to_prolog("The inclusion-exclusion principle for two sets states that the union of A and B is given by A + B minus their intersection.", inclusion_exclusion(A, B, Intersection, Union) :- Union is A + B - Intersection).

% Converts a Prolog rule into a human-readable statement.
prolog_to_cnl(permutation(N, R, P) :- N >= R, factorial(N, F1), factorial(N - R, F2), P is F1 // F2, "The number of ways to arrange R objects from a set of N objects is given by permutations.").

prolog_to_cnl(combination(N, R, C) :- N >= R, factorial(N, F1), factorial(R, F2), factorial(N - R, F3), C is F1 // (F2 * F3), "The number of ways to choose R objects from a set of N objects is given by combinations.").

prolog_to_cnl(inclusion_exclusion(A, B, Intersection, Union) :- Union is A + B - Intersection, "The inclusion-exclusion principle for two sets states that the union of A and B is given by A + B minus their intersection.").

% --- Example Usage ---

% validate_statement("There are 45 ways to choose 2 elements from a set of 10.", intent_data{primary_intent: solve_problem}).
% validate_permutation_statement("The number of permutations of 5 objects taken 3 at a time is 60.", intent_data{primary_intent: solve_problem}).

