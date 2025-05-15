#include <vector>
#include <string>
#include <tuple>
#include <algorithm> // For std::sort
#include <functional> // For std::function
#include <limits>     // For std::numeric_limits

// Pybind11 headers
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For automatic conversion of std::vector, std::tuple, etc.

// Helper structure to hold item data along with its efficiency for sorting
struct ItemWithEfficiency {
    std::string name;
    int price;
    double total_weight;
    double efficiency;

    ItemWithEfficiency(std::string n, int p, double w)
        : name(std::move(n)), price(p), total_weight(w) {
        if (price == 0) {
            if (total_weight > 0) {
                efficiency = std::numeric_limits<double>::infinity();
            } else if (total_weight == 0) {
                efficiency = 0.0;
            } else { // total_weight < 0
                efficiency = -std::numeric_limits<double>::infinity();
            }
        } else {
            efficiency = total_weight / static_cast<double>(price);
        }
    }
};

// The core C++ implementation
// Renamed to avoid direct conflict if we were to also expose the Python version's name directly
// This C++ function will be called internally by the Python interface.
std::tuple<std::vector<std::string>, int, double>
optimize_items_cpp_logic(
    int budget,
    const std::vector<std::tuple<std::string, int, double>>& input_items_data,
    int max_items_allowed) {

    std::vector<ItemWithEfficiency> items_list;
    items_list.reserve(input_items_data.size());
    for (const auto& item_tuple : input_items_data) {
        items_list.emplace_back(std::get<0>(item_tuple), std::get<1>(item_tuple), std::get<2>(item_tuple));
    }

    std::sort(items_list.begin(), items_list.end(), [](const ItemWithEfficiency& a, const ItemWithEfficiency& b) {
        return a.efficiency > b.efficiency;
    });

    std::vector<std::string> best_combination;
    double best_weight = 0.0;
    int best_price = 0;

    std::vector<std::string> current_items_stack;

    std::function<void(size_t, int, double)> backtrack =
        [&](size_t start_idx, int current_price, double current_weight) {
        if (current_weight > best_weight && current_price <= budget) {
            best_combination = current_items_stack;
            best_weight = current_weight;
            best_price = current_price;
        }

        if (start_idx >= items_list.size() || current_items_stack.size() >= static_cast<size_t>(max_items_allowed)) {
            return;
        }

        for (size_t i = start_idx; i < items_list.size(); ++i) {
            const auto& item = items_list[i];
            if (current_price + item.price > budget) {
                continue;
            }
            current_items_stack.push_back(item.name);
            backtrack(
                i + 1,
                current_price + item.price,
                current_weight + item.total_weight);
            current_items_stack.pop_back();
        }
    };

    backtrack(0, 0, 0.0);

    return std::make_tuple(best_combination, best_price, best_weight);
}

// pybind11 module definition
namespace py = pybind11;

PYBIND11_MODULE(knapsack_optimizer_cpp, m) { // Module name seen by Python: import knapsack_optimizer_cpp
    m.doc() = "Pybind11 plugin for the knapsack-like item optimizer"; // Optional module docstring

    m.def("solve_knapsack_cpp", // Function name exposed to Python
          &optimize_items_cpp_logic,
          "Solves the knapsack-like problem to find optimal items using C++.",
          py::arg("budget"),
          py::arg("input_items_data"), // std::vector<std::tuple<std::string, int, double>>
          py::arg("max_items_allowed")
    );
}