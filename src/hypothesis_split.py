"""
hypothesis_split.py — 假设拆分与具体化引擎

核心原则：
- 一个假设只能包含 1 个 IV + 1 个 DV + 1 个机制链
- 多变量问题自动拆成 2-3 个子假设
- 每个假设包含可拟合参数和模型对比
- 结构化 12 字段输出格式
"""

from typing import Any, Dict, List, Optional, Tuple


# ── 假设模板注册表 ──────────────────────────────────────────────────────

HYPOTHESIS_TEMPLATES: List[Dict[str, Any]] = [
    # ── H1: D* 归一化距表面距离 ──
    {
        "hid": "H1",
        "title": "归一化距表面距离 D* 调控孔隙诱导疲劳裂纹起裂风险的假设",
        "target_ivs": ["pore_size", "distance_to_surface"],
        "target_dvs": ["crack_initiation_site", "Nf_life"],
        "triggers": ["pore_size", "distance_to_surface", "pore_location", "defect", "孔隙", "缺陷", "距表面"],
        "hypothesis": (
            "在 polished/machined L-PBF Ti-6Al-4V 中，归一化距表面距离 "
            "D* = distance_to_surface / √area 越小的孔隙，"
            "其边缘应力集中与自由表面应力场的叠加效应越强，"
            "越可能成为疲劳裂纹起裂源，并导致相应的 Nf 降低。"
        ),
        "core_variable": "D* = distance_to_surface / √area",
        "core_variable_cn": "归一化距表面距离",
        "main_dv": "crack_initiation_site（裂纹起裂位置）",
        "auxiliary_dv": "Nf（疲劳寿命）",
        "condition_boundary": "polished/machined 表面；SR 热处理；R=0.1；室温",
        "mechanism_chain": (
            "近表面孔隙 (D* small) → 孔隙边缘应力集中与自由表面应力场叠加 "
            "→ 局部有效应力幅增大 → 裂纹在孔隙-表面最短路径处提前起裂 "
            "→ Ni 降低 → Nf 降低"
        ),
        "fittable_model": (
            "logit(P_initiation) = β₀ + β₁ · log(√area) + β₂ · D*  "
            "其中 P_initiation 为孔隙成为起裂源的概率（逻辑回归）"
        ),
        "prediction_direction": (
            "D* ↓ → 起裂概率 ↑ (β₂ < 0)；"
            "D* ↓ → Nf ↓；"
            "D* 的解释力应独立于 √area"
        ),
        "support_criteria": [
            "逻辑回归中 β₂ 显著为负 (p < 0.05)",
            "加入 D* 后模型 AUC 提升 > 0.05",
            "SEM 确认的起裂源与 micro-CT 定位孔隙的空间对应率 > 70%",
        ],
        "falsification_criteria": [
            "D* 与起裂位置无显著相关 (p > 0.10)",
            "加入 D* 后模型 AIC/BIC 未改善",
            "起裂源与近表面孔隙的对应率 < 30%",
        ],
        "experiment_path": (
            "micro-CT 疲劳前扫描 → 提取每个孔隙的 √area 和 distance_to_surface → "
            "计算 D* → HCF 试验 → SEM fractography 确认起裂源 → "
            "逻辑回归拟合起裂概率 vs D* + √area"
        ),
        "model_comparison": (
            "Model A: logit(P) = β₀ + β₁·log(√area)\n"
            "Model B: logit(P) = β₀ + β₁·log(√area) + β₂·D*\n"
            "预期 Model B 优于 Model A (ΔAIC > 4)"
        ),
        "score_total": 44,
        "score_detail": {"specificity":5, "clarity":5, "mechanism":5, "testability":5,
                         "falsifiability":5, "model":4, "evidence":3, "feasibility":4,
                         "experiment":4, "quantification":4},
    },

    # ── H2: 表面粗糙度掩盖孔隙效应 ──
    {
        "hid": "H2",
        "title": "as-built 表面粗糙度掩盖内部孔隙寿命效应的条件边界假设",
        "target_ivs": ["surface_roughness_Ra", "surface_state"],
        "target_dvs": ["Nf_life", "crack_initiation_site"],
        "triggers": ["roughness", "surface", "as-built", "表面", "粗糙", "ra"],
        "hypothesis": (
            "在 as-built L-PBF Ti-6Al-4V 中，表面粗糙度 Ra/Rz 较高 (Ra > 10μm) 时，"
            "表面缺口效应（Kt ≈ 2-3）主导疲劳裂纹起裂，"
            "内部孔隙尺寸/位置对 Nf 的解释力被显著削弱。"
            "当表面加工至 Ra < 1μm 后，内部孔隙对起裂和 Nf 的影响重新成为主导。"
        ),
        "core_variable": "surface_state (as-built / polished / machined)",
        "core_variable_cn": "表面状态 / 表面粗糙度等级",
        "main_dv": "Nf（疲劳寿命）",
        "auxiliary_dv": "crack_initiation_site（起裂源类型：表面vs孔隙）",
        "condition_boundary": "L-PBF Ti-6Al-4V；SR 热处理；R=0.1；室温",
        "mechanism_chain": (
            "as-built 表面 (Ra>10μm) → 表面粗糙峰根部应力集中 (Kt≈2-3) "
            "→ 表面优先起裂 (vs 内部孔隙) → Nf 由表面粗糙度控制 "
            "→ 内部孔隙对 Nf 的解释力被掩盖"
        ),
        "fittable_model": (
            "交互效应回归: log(Nf) = β₀ + β₁·log(Ra) + β₂·log(√area_max) "
            "+ β₃·surface_state + β₄·log(Ra)×log(√area_max)"
        ),
        "prediction_direction": (
            "as-built: β₁ (Ra) 显著, β₂ (√area) 不显著；"
            "polished: β₂ 显著, β₁ 不显著；"
            "交互项 β₄ < 0（表面状态削弱孔隙效应）"
        ),
        "support_criteria": [
            "as-built 组起裂源 > 80% 为表面特征",
            "as-built 组 Nf 回归中 Ra 的 R² > 0.4 且 √area 的 R² < 0.1",
            "polished 组起裂源 > 60% 为孔隙",
            "交互项 β₄ 显著 (p < 0.05)",
        ],
        "falsification_criteria": [
            "as-built 组起裂源仍主要为孔隙而非表面",
            "as-built 回归中 √area 的 R² > Ra 的 R²",
            "不同表面状态下起裂源分布无显著差异 (χ² test p > 0.05)",
        ],
        "experiment_path": (
            "同一批次材料制备 as-built / polished / machined 三组试样 → "
            "Ra/Rz 测量 → micro-CT → HCF 多应力水平 → "
            "SEM 断口确认每组起裂源分布 → 分组回归比较 Ra vs √area 的解释力"
        ),
        "model_comparison": (
            "as-built 组: log(Nf) = f(Ra) vs log(Nf) = f(√area)\n"
            "polished 组: log(Nf) = f(Ra) vs log(Nf) = f(√area)\n"
            "预期 as-built 组 Ra 模型更优，polished 组 √area 模型更优"
        ),
        "score_total": 43,
        "score_detail": {"specificity":5, "clarity":5, "mechanism":5, "testability":5,
                         "falsifiability":5, "model":4, "evidence":4, "feasibility":4,
                         "experiment":4, "quantification":3},
    },

    # ── H3: D* 增强模型 ──
    {
        "hid": "H3",
        "title": "加入 D* 的缺陷-寿命模型比单独 √area 模型更能解释疲劳寿命 Nf 的假设",
        "target_ivs": ["pore_size", "distance_to_surface"],
        "target_dvs": ["Nf_life"],
        "triggers": ["pore_size", "distance_to_surface", "Nf", "fatigue_life", "孔隙", "疲劳寿命", "模型"],
        "hypothesis": (
            "在控制应力幅 σa、应力比 R 和表面状态 (polished) 后，"
            "包含 √area 和 D* 的 S-N 修正模型 (Model B) "
            "比仅包含 √area 的模型 (Model A) 具有更高的拟合优度 (R²) "
            "和更低的 AIC/BIC，说明孔隙位置（距表面距离）对疲劳寿命的调节作用不可忽略。"
        ),
        "core_variable": "√area + D* (D* = distance_to_surface / √area)",
        "core_variable_cn": "缺陷尺寸 + 归一化位置",
        "main_dv": "log(Nf)（对数疲劳寿命）",
        "auxiliary_dv": "—",
        "condition_boundary": "polished 表面；SR 处理；R=0.1；σa 多水平",
        "mechanism_chain": (
            "√area → 局部应力集中幅值 | D* → 自由表面叠加效应 → "
            "共同决定起裂驱动力 → 共同解释 Nf 变异"
        ),
        "fittable_model": (
            "Model A: log(Nf) = β₀ + β₁·log(σa) + β₂·log(√area)\n"
            "Model B: log(Nf) = β₀ + β₁·log(σa) + β₂·log(√area) + β₃·D*\n"
            "Model C: log(Nf) = β₀ + β₁·log(σa) + β₂·log(√area) + β₃·D* + β₄·surface_state"
        ),
        "prediction_direction": (
            "Model B vs A: ΔR² > 0.05, ΔAIC < -4 (支持 H3); "
            "Model C vs B: ΔR² > 0.03, ΔAIC < -3 (支持表面状态额外贡献)"
        ),
        "support_criteria": [
            "Model B 的 R² 显著高于 Model A (F-test p < 0.05)",
            "β₃ (D*) 显著为负 (p < 0.05)",
            "Model B 的 AIC 较 Model A 降低 > 4 个单位",
            "留一交叉验证 RMSE 降低 > 10%",
        ],
        "falsification_criteria": [
            "Model B 的 R² 提升 < 0.02",
            "β₃ 不显著 (p > 0.10)",
            "Model B 的 AIC 未改善",
            "Model C 未进一步改善",
        ],
        "experiment_path": (
            "收集包含 √area、distance_to_surface、surface_state、σa、Nf 的结构化数据 → "
            "计算 D* → 拟合 Model A/B/C → 比较 R²/AIC/RMSE"
        ),
        "model_comparison": (
            "Model A: 仅 σa + √area  (baseline)\n"
            "Model B: + D* （验证位置效应）\n"
            "Model C: + D* + surface_state （验证表面状态调制）\n"
            "评价指标对比: R², AIC, BIC, ΔRMSE"
        ),
        "score_total": 45,
        "score_detail": {"specificity":5, "clarity":4, "mechanism":4, "testability":5,
                         "falsifiability":5, "model":5, "evidence":3, "feasibility":4,
                         "experiment":4, "quantification":5},
    },
]


# ── 假设拆分引擎 ──────────────────────────────────────────────────────

def detect_variable_complexity(question: str, ind_var: Optional[str], dep_var: Optional[str]) -> bool:
    """检测问题是否涉及多变量、多机制，需要假设拆分。"""
    if not question:
        return False
    q = question.lower()
    multi_indicators = ["和", "与", "及", "以及", "共同", "耦合", "交互",
                        "and", "with", "coupled", "combined", "joint", "interaction"]
    multi_vars = sum(1 for m in ["pore", "roughness", "surface", "defect",
                                  "distance", "location", "state", "ratio",
                                  "heat", "microstructure"] if m in q)
    has_connector = any(m in q for m in multi_indicators)
    return has_connector or multi_vars >= 3


def match_hypothesis_templates(question: str, ind_var: Optional[str], dep_var: Optional[str]) -> List[Dict[str, Any]]:
    """根据用户问题和变量匹配适合的假设模板。"""
    q = (question or "").lower()
    iv = (ind_var or "").lower()
    dv = (dep_var or "").lower()
    combined = f"{q} {iv} {dv}"

    matched = []
    for tmpl in HYPOTHESIS_TEMPLATES:
        score = 0
        for trigger in tmpl["triggers"]:
            if trigger.lower() in combined:
                score += 1
        if score >= 1:
            matched.append((score, tmpl))

    # 按匹配度排序
    matched.sort(key=lambda x: -x[0])
    return [m[1] for m in matched]


def format_split_hypotheses(templates: List[Dict[str, Any]]) -> str:
    """将拆分的假设格式化为结构化 Markdown。"""
    lines = []
    lines.append("## 拆分候选假设\n")
    lines.append("> 检测到问题涉及多变量，已拆分为以下子假设：\n\n")

    for tmpl in templates:
        hid = tmpl["hid"]
        title = tmpl["title"]
        hypothesis = tmpl["hypothesis"]
        core_var = tmpl["core_variable"]
        main_dv = tmpl["main_dv"]
        cond = tmpl["condition_boundary"]
        mechanism = tmpl["mechanism_chain"]
        model = tmpl["fittable_model"]
        prediction = tmpl["prediction_direction"]
        support = tmpl["support_criteria"]
        falsify = tmpl["falsification_criteria"]
        experiment = tmpl["experiment_path"]
        model_cmp = tmpl["model_comparison"]
        score = tmpl["score_total"]

        lines.append(f"### {hid}: {title}\n")
        lines.append(f"**假设陈述**: {hypothesis}\n\n")
        lines.append(f"**核心变量**: {core_var}\n")
        lines.append(f"**主要因变量**: {main_dv}\n")
        lines.append(f"**条件边界**: {cond}\n\n")
        lines.append("**机制链**:\n```\n" + mechanism + "\n```\n")
        lines.append(f"**可拟合模型**: `{model}`\n\n")
        lines.append(f"**预测方向**: {prediction}\n\n")

        lines.append("**支持判据**:\n")
        for c in support:
            lines.append(f"- {c}\n")
        lines.append("\n")

        lines.append("**推翻判据**:\n")
        for c in falsify:
            lines.append(f"- {c}\n")
        lines.append("\n")

        lines.append(f"**实验验证路径**: {experiment}\n\n")
        lines.append("**模型对比**:\n```\n" + model_cmp + "\n```\n")

        # 评分可视化
        detail = tmpl["score_detail"]
        dim_names = {"specificity":"具体性", "clarity":"清晰度", "mechanism":"机制",
                     "testability":"可验证性", "falsifiability":"可推翻性", "model":"模型",
                     "evidence":"证据", "feasibility":"可行性", "experiment":"实验",
                     "quantification":"量化"}
        bar = "█" * (score // 5) + "░" * (max(0, 9 - score // 5))
        lines.append(f"**假设评分**: {score}/50 {bar}\n")
        for key, cn in dim_names.items():
            s = detail.get(key, 3)
            bar2 = "█" * s + "░" * (max(0, 5 - s))
            lines.append(f"- {cn}: {s}/5 {bar2}\n")
        lines.append("\n---\n")

    # 末尾总结：假设选择建议
    lines.append("### 假设选择建议\n")
    lines.append("| 假设 | 适用场景 | 实验难度 | 预期产出 |\n")
    lines.append("|---|---|---|---|\n")
    lines.append("| H1 | 验证孔隙位置调控起裂风险 | 中等 (micro-CT + SEM) | 逻辑回归模型 + 起裂概率预测 |\n")
    lines.append("| H2 | 验证表面粗糙度 vs 孔隙竞争 | 中等 (表面处理 + HCF) | 条件边界值 + 竞争失效图 |\n")
    lines.append("| H3 | 验证 D* 改善寿命预测 | 较低 (数据拟合) | Model A/B/C 性能对比表 |\n")

    return "".join(lines)


def generate_split_hypotheses(question: str, ind_var: Optional[str], dep_var: Optional[str]) -> Optional[str]:
    """
    主入口：根据用户问题生成拆分假设。

    如果问题涉及多变量，自动匹配模板并拆分。
    如果问题只涉及单一变量对，回退到原模板。

    Args:
        question: 用户原始问题
        ind_var: 识别到的自变量
        dep_var: 识别到的因变量

    Returns:
        结构化的假设 Markdown 文本，或 None
    """
    needs_split = detect_variable_complexity(question, ind_var, dep_var)

    if needs_split:
        matched = match_hypothesis_templates(question, ind_var, dep_var)
        if matched:
            return format_split_hypotheses(matched)

    return None


# ── 旧假设的替换升级 ─────────────────────────────────────────────────

def replace_old_hypothesis(question: str, ind_var: str, dep_var: str) -> Tuple[bool, Optional[str]]:
    """
    检测并替换旧的大而全假设。

    Returns:
        (was_replaced, new_hypothesis_text)
    """
    # 检查是否是典型的"多变量合一"问题
    iv_lower = (ind_var or "").lower()
    dv_lower = (dep_var or "").lower()

    complex_triggers = [
        ("pore_size", "fatigue_life"),
        ("surface_roughness", "fatigue_life"),
        ("pore_location", "fatigue_life"),
    ]
    is_complex = (ind_var, dep_var) in complex_triggers or (dep_var, ind_var) in complex_triggers

    if not is_complex:
        return False, None

    # 检查问题是否明确包含多变量
    if question:
        q = question.lower()
        multi_keywords = ["和", "与", "共同", "耦合", "交互", "together",
                          "combined", "coupled", "interaction",
                          "pore size", "surface roughness", "distance",
                          "孔隙", "距表面", "表面状态", "表面粗糙", "疲劳寿命"]
        has_multi = sum(1 for kw in multi_keywords if kw in q) >= 2
        if has_multi:
            new_hyp = generate_split_hypotheses(question, ind_var, dep_var)
            if new_hyp:
                return True, new_hyp

    return False, None
