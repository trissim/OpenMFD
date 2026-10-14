# Slimmed-down plotting script — reads data.csv directly

library(tidyverse)
library(ggbeeswarm)
library(ggsignif)
library(lme4)
library(lmerTest)
library(emmeans)

# ── User options ──
show_pairwise_bars <- TRUE   # set FALSE to hide Tukey-style comparison brackets

# Which plots to save (edit this list to choose)
plots_to_save <- c(
  "dapi_count",
  "pre_cell_count",
  #"post_cell_count",
  "pre_per_dapi",
  #"post_per_dapi",
  #"post_per_pre",
  "total_axon_count",
  "neurite_per_pre",
  #"neurite_per_post",
  #"axon_normalized",
  "neurite_per_pre_normalized"
  #,"neurite_per_post_normalized"
)

# ── Manual outlier removal ──
# Applied on top of the `outlier` column already set in data.csv.
# Format: "<plate>_<well>", e.g. manual_outliers <- c("p1_R06C05", "p3_R05C02")

manual_outliers <- c()

condition_levels <- c("DMSO", "FC-A", "F04", "EpoB", "EpoB + FCA")
geno_colors <- c(
  "DMSO" = "#1f77b4",
  "FC-A" = "#ff7f0e",
  "F04" = "#2ca02c",
  "EpoB" = "#d62728",
  "EpoB + FCA" = "#9467bd"
)
plate_colors <- c("p1" = "#66c2a5", "p2" = "#fc8d62", "p3" = "#8da0cb", "p4" = "#e78ac3")

# ============================================================================
# Data Loading and Processing
# ============================================================================

full_data <- read.csv("data.csv") |>
  mutate(
    condition = factor(condition, levels = condition_levels),
    key = paste(plate, well, sep = "_"),
    csv_outlier = outlier,
    manual_outlier = key %in% manual_outliers,
    pre_per_dapi = pre_cell_count / dapi_count,
    post_per_dapi = post_cell_count / dapi_count,
    post_per_pre = post_cell_count / pre_cell_count,
    neurite_per_pre = total_axon_count / pre_cell_count,
    neurite_per_post = total_axon_count / post_cell_count
  )

data <- full_data |>
  filter(!csv_outlier, !manual_outlier) |>
  select(-key, -csv_outlier, -manual_outlier, -outlier)

# ── Per-plate DMSO-normalized metrics ──

dmso_means <- data |>
  filter(condition == "DMSO") |>
  group_by(plate) |>
  summarise(
    dmso_axon = mean(total_axon_count),
    dmso_neurite_pre = mean(neurite_per_pre),
    dmso_neurite_post = mean(neurite_per_post),
    .groups = "drop"
  )

data <- data |>
  left_join(dmso_means, by = "plate") |>
  mutate(
    axon_normalized = total_axon_count / dmso_axon,
    neurite_per_pre_normalized = neurite_per_pre / dmso_neurite_pre,
    neurite_per_post_normalized = neurite_per_post / dmso_neurite_post
  ) |>
  select(-dmso_axon, -dmso_neurite_pre, -dmso_neurite_post)

# ============================================================================
# Statistical Analysis
# ============================================================================

summary_data <- data |>
  group_by(condition) |>
  summarise(
    n = n(),
    across(where(is.numeric), list(mean = mean, sd = sd), na.rm = TRUE, .names = "{.col}_{.fn}")
  )

anova_results <- data |>
  pivot_longer(
    cols = c(dapi_count, pre_cell_count, pre_per_dapi, post_per_dapi, post_per_pre, total_axon_count, neurite_per_pre, neurite_per_post),
    names_to = "metric",
    values_to = "value"
  ) |>
  group_by(metric) |>
  nest() |>
  mutate(
    aov_result = map(data, ~aov(value ~ condition, data = .x)),
    p_value = map_dbl(aov_result, ~summary(.x)[[1]][1, "Pr(>F)"]),
    f_stat = map_dbl(aov_result, ~summary(.x)[[1]][1, "F value"])
  ) |>
  select(metric, p_value, f_stat)

pairwise_neurite_post <- emmeans(
  lmer(neurite_per_post ~ condition + (1 | plate), data = data),
  pairwise ~ condition
)

# ============================================================================
# Plotting
# ============================================================================

metrics <- list(
  dapi_count = "DAPI Count",
  pre_cell_count = "Pre-axotomy Cell Counts",
  post_cell_count = "Post-axotomy Cell Counts",
  pre_per_dapi = "Pre / DAPI",
  post_per_dapi = "Post / DAPI",
  post_per_pre = "Post / Pre",
  total_axon_count = "Total Axon Length",
  neurite_per_pre = "Axon / Pre",
  neurite_per_post = "Axon / Post *",
  axon_normalized = "Axon / Plate DMSO Mean",
  neurite_per_pre_normalized = "Axon / Pre (norm to DMSO)",
  neurite_per_post_normalized = "Axon / Post (norm to DMSO)"
)

# ── Pairwise comparisons for all metrics (linear mixed model, plate as random effect) ──
all_pairwise <- map(names(metrics), function(m) {
  fml <- as.formula(paste0(m, " ~ condition + (1 | plate)"))
  fit <- lmer(fml, data = data)
  emm <- emmeans(fit, pairwise ~ condition)
  pw_df <- summary(emm$contrasts)
  comparisons <- map(pw_df$contrast, function(cname) {
    parts <- strsplit(cname, " - ")[[1]]
    c(gsub("^\\(|\\)$", "", trimws(parts[1])),
      gsub("^\\(|\\)$", "", trimws(parts[2])))
  })
  sig_labels <- case_when(
    pw_df$p.value < 0.001 ~ "***",
    pw_df$p.value < 0.01  ~ "**",
    pw_df$p.value < 0.05  ~ "*",
    TRUE                  ~ "n.s."
  )
  sig_idx <- sig_labels != "n.s."
  list(
    comparisons = comparisons[sig_idx],
    labels = sig_labels[sig_idx]
  )
}) |> set_names(names(metrics))

make_plot <- function(df, metric_col, colors, pairwise_list) {
  summ <- df |>
    group_by(condition) |>
    summarise(mean = mean(.data[[metric_col]]), sd = sd(.data[[metric_col]]))

  p <- ggplot(df, aes(x = condition, y = .data[[metric_col]], fill = condition)) +
    geom_col(data = summ, aes(y = mean), alpha = 0.7, color = "black", linewidth = 0.8) +
    geom_errorbar(
      data = summ,
      aes(y = mean, ymin = mean - sd, ymax = mean + sd),
      width = 0.2, linewidth = 0.8, color = "black"
    ) +
    geom_quasirandom(width = 0.2, size = 2, alpha = 0.6, aes(color = plate)) +
    scale_fill_manual(values = colors) +
    scale_color_manual(values = plate_colors) +
    labs(title = metrics[[metric_col]], y = NULL, x = NULL, color = "Plate") +
    theme_minimal() +
    theme(
      axis.text = element_text(size = 25, color = "black"),
      axis.title.x = element_blank(),
      plot.title = element_text(size = 29, face = "bold", hjust = 0.5),
      panel.grid = element_blank(),
      legend.position = "right",
      axis.text.x = element_text(angle = 45, hjust = 1)
    )

  if (show_pairwise_bars && length(pairwise_list$comparisons) > 0) {
    p <- p + geom_signif(
      comparisons = pairwise_list$comparisons,
      annotations = pairwise_list$labels,
      map_signif_level = FALSE,
      tip_length = 0.01,
      step_increase = 0.05
    )
  }

  p
}

plots <- imap(metrics, ~ make_plot(data, .y, geno_colors, all_pairwise[[.y]]))

# ============================================================================
# Save Outputs
# ============================================================================

if (!dir.exists("Plots")) dir.create("Plots")
if (!dir.exists("Output")) dir.create("Output")

write_csv(summary_data, "Output/summary_statistics.csv")
write_csv(anova_results, "Output/anova_results.csv")

iwalk(plots[plots_to_save], ~ ggsave(
  filename = file.path("Plots", sprintf("%02d_%s.png", which(plots_to_save == .y), .y)),
  plot = .x, width = 10, height = 7, dpi = 300
))

pdf("Plots/all_plots.pdf", width = 10, height = 7)
walk(plots[plots_to_save], print)
dev.off()

# ============================================================================
# Display Results
# ============================================================================

summary_data
anova_results
pairwise_neurite_post
