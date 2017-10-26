import random
from typing import Set, Iterable, Tuple


class SAT:
    threshold = 0.7

    def __init__(self, file):
        with open(file) as reader:
            self.lines = [[int(val) for val in line.split()] for line in reader.readlines()]
        self.vars: Set[int] = set()
        for line in self.lines:
            self.vars.update(set([abs(var) for var in line]))
        self.vars_to_indices = {var: self.get_ind(ind) for (ind, var) in enumerate(self.vars)}
        self.indices_to_vars = {self.get_ind(ind): var for (ind, var) in enumerate(self.vars)}

        self.iter_count = 0
        # One dictionary for each clause. Var: True or Var: False
        self.clauses = [{self.vars_to_indices[abs(var)]: var >= 0 for var in line} for line in self.lines]
        self.final_model = None
        print('Clauses: %s' + str(self.clauses))
        print('Variables: %s' + str(self.vars))
        print('indices to vars: ' + str(self.indices_to_vars))
        print('vars to indices: ' + str(self.vars_to_indices))

    def reset_stats(self):
        self.iter_count = 0

    def print_stats(self):
        print('Iterations needed: %d' % self.iter_count)

    def gsat(self) -> list:
        self.reset_stats()
        model = [None] + [random.choice([True, False]) for _ in range(len(self.vars))]
        while not self.assignment_complete(model):
            self.iter_count += 1
            if random.random() > SAT.threshold:
                rand_var = random.choice(list(self.vars_to_indices.values()))
                model[rand_var] = not model[rand_var]
            else:
                var_to_flip = self.choose_best_variable(model)
                model[var_to_flip] = not model[var_to_flip]
            print('unsatisfied clauses: %d' % len(self.get_unsatisfied_clauses(model)))

        self.print_stats()
        self.final_model = model  # for write_solution
        return model

    def walksat(self) -> list:
        self.reset_stats()
        model = [None] + [random.choice([True, False]) for _ in range(len(self.vars))]
        while not self.assignment_complete(model):
            self.iter_count += 1
            if random.random() > SAT.threshold:
                rand_var = random.choice(list(self.vars_to_indices.values()))
                model[rand_var] = not model[rand_var]
            else:
                var_to_flip = self.choose_candidate_variables(model)
                model[var_to_flip] = not model[var_to_flip]
        self.print_stats()
        self.final_model = model
        return model

    def choose_candidate_variables(self, model) -> int:
        """
        For WalkSAT
        :param model: current model
        :return: The index of one candidate variable
        """
        unsatisfied_clauses = self.get_unsatisfied_clauses(model)
        print('Unsatisfied clauses: %d' % len(unsatisfied_clauses))
        clause_chosen: dict = random.choice(unsatisfied_clauses)
        return self.choose_best_variable(model, clause_chosen.keys())

    def get_unsatisfied_clauses(self, model):
        unsatisfied_clauses = []
        for c in self.clauses:
            if not self.clause_is_satisfied(model, c):
                unsatisfied_clauses.append(c)
        return unsatisfied_clauses

    def write_solution(self, filename):
        lines = []
        for ind, val in enumerate(self.final_model):
            if ind != 0:  # skip 0 indexing!
                var = self.indices_to_vars[ind]
                if not val:
                    var = -var
                lines.append(str(var))

        with open(filename, 'w') as file_writer:
            file_writer.writelines('\n'.join(lines))

    def assignment_complete(self, model):
        for c in self.clauses:
            clause_is_satisfied = self.clause_is_satisfied(model, c)
            if not clause_is_satisfied:  # break early if one the clauses is not satisfied
                return False
        return True

    def choose_best_variable(self, model: list, candidate_set=None):
        """
        Choose the variable that maximizes number of clauses satisfied
        :param model: current model
        :param candidate_set: vars to consider when maximizing the number of clauses satisfied
        """
        all_counts, max_count = self.count_clauses_satisfied_if_all_flipped(
            model=model,
            candidate_variables=self.vars_to_indices.values() if candidate_set is None else candidate_set
        )
        possible_vars = all_counts[max_count]
        return random.choice(possible_vars)

    def count_clauses_satisfied_if_all_flipped(self, model: list, candidate_variables: Iterable) -> Tuple[dict, int]:
        max_count = 0
        all_counts = {}
        for var in candidate_variables:
            curr_count = self.count_clauses_satisfied_if_flipped(model, var)
            if curr_count not in all_counts:
                all_counts[curr_count] = []
            all_counts[curr_count].append(var)
            i = max_count
            max_count = max(max_count, curr_count)
            assert max_count >= i
        return all_counts, max_count

    def count_clauses_satisfied_if_flipped(self, model: list, var: int):
        """
        Flip the bit, count the number of clauses satisfied by that model, and unflip the bit
        """
        model[var] = not model[var]
        satisfied_count = self.count_clauses_satisfied(model)
        model[var] = not model[var]
        return satisfied_count

    def count_clauses_satisfied(self, model: list):
        """
        count the number of clauses satisfied by this model
        :param model:
        :return:
        """
        count = 0
        for c in self.clauses:
            clause_is_satisfied = self.clause_is_satisfied(model, c)
            if clause_is_satisfied:
                count += 1
        return count

    def clause_is_satisfied(self, model: list, c: dict):
        return any([model[var] == c[var] for var in c])

    @staticmethod
    def get_ind(ind):
        """
        LOOP ONLY IF ABSOLUTELY NEEDED.
        Indices start at 1. Use when looping.
        """
        return ind + 1
