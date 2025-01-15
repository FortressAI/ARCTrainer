% Domain-specific rules for IMO Algebra problems

% --- Algebraic Principles and Theorems ---

% Validates the application of the AM-GM inequality using language games.
validate_am_gm(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: validate_theorem},
    play_language_game(
        Statement,
        game_data{
            type: "validate_theorem",
            theorem: "AM-GM Inequality",
            terms: ["arithmetic mean", "geometric mean"],
            validation_logic: apply_am_gm
        }
    ).

validate_cauchy_schwarz(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: validate_theorem},
    play_language_game(
        Statement,
        game_data{
            type: "validate_theorem",
            theorem: "Cauchy-Schwarz Inequality",
            terms: ["dot product", "vector magnitude"],
            validation_logic: apply_cauchy_schwarz
        }
    ).

validate_rearrangement_inequality(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: validate_theorem},
    play_language_game(
        Statement,
        game_data{
            type: "validate_theorem",
            theorem: "Rearrangement Inequality",
            terms: ["permutation", "sorted order"],
            validation_logic: apply_rearrangement
        }
    ).

% --- Validation Rules ---

% Validate a statement about solving an equation.
validate_statement(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: solve_problem},
    play_language_game(
        Statement,
        game_data{
            type: "solve_equation",
            parsing_logic: parse_equation,
            solving_logic: solve_equation
        }
    ).

% --- Algebraic Operations ---

% Simplifies an algebraic expression using a language game.
simplify_expression(Expression, SimplifiedExpression) :-
    play_language_game(
        Expression,
        game_data{
            type: "simplify_expression",
            simplification_logic: simplify_logic,
            result_var: SimplifiedExpression
        }
    ).

% Factors a polynomial using a language game.
factor_polynomial(Polynomial, Factors) :-
    play_language_game(
        Polynomial,
        game_data{
            type: "factor_polynomial",
            factoring_logic: factor_logic,
            result_var: Factors
        }
    ).

% Expands an algebraic expression using a language game.
expand_expression(Expression, ExpandedExpression) :-
    play_language_game(
        Expression,
        game_data{
            type: "expand_expression",
            expansion_logic: expand_logic,
            result_var: ExpandedExpression
        }
    ).

% --- Helper Logic for Language Games ---

% Applies the AM-GM theorem validation logic.
apply_am_gm(Term1, Term2) :-
    arithmetic_mean(Term1, Term2, AM),
    geometric_mean(Term1, Term2, GM),
    AM >= GM.

% Example: Calculates the arithmetic mean.
arithmetic_mean(Term1, Term2, Result) :-
    Result is (Term1 + Term2) / 2.

% Example: Calculates the geometric mean.
geometric_mean(Term1, Term2, Result) :-
    Result is sqrt(Term1 * Term2).

% --- Example Usage ---

% validate_statement("The solution to the equation 2x + 5 = 9 is x = 2.", intent_data{primary_intent: solve_problem}).
% simplify_expression("2*x + x", Simplified). -> Simplified = "3*x"
% factor_polynomial("x^2 - 4", Factors). -> Factors = "(x - 2)(x + 2)"
% expand_expression("(x + 1)(x - 1)", Expanded). -> Expanded = "x^2 - 1"
