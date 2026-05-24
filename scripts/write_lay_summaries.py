#!/usr/bin/env python3
"""Write lay summary drafts into publications.yaml."""

import yaml
import os

YAML_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "publications.yaml")

DRAFTS = {
    "attia-2026-paleos": (
        "To understand what rocky exoplanets are made of, we need accurate descriptions"
        " of how materials behave under extreme pressures and temperatures. PALEOS is an"
        " open-source toolkit that provides these descriptions for iron, rock, and water"
        " across 17 different material phases, from solid to fully molten. Applying it to"
        " observed exoplanets reveals that two planets with identical size and mass could"
        " be in completely different states: one frozen solid, the other hosting a deep"
        " magma ocean with an active magnetic field."
    ),
    "van-dijk-2026-onset": (
        "After the Moon-forming impact, Earth was covered in a global magma ocean beneath"
        " a thick atmosphere. We show that tidal heating from the young Moon, combined with"
        " greenhouse warming from outgassed volatiles, could have kept Earth's surface"
        " molten for anywhere from 30 to 500 million years depending on the chemistry of"
        " the mantle. The interplay between tides and atmospheric composition also produces"
        " distinctive chemical signatures that could help constrain the early conditions"
        " that led to habitability."
    ),
    "nicholls-2026-volatile-rich": (
        "The exoplanet L 98-59 d is surprisingly large for its mass, suggesting it holds"
        " substantial volatiles, but whether it is a miniature gas planet or a water world"
        " has been unclear. By simulating its evolution from birth to present day, we find"
        " neither scenario fits; instead, its atmosphere is sustained by a permanent magma"
        " ocean releasing sulfur and hydrogen over billions of years. This points to a new"
        " evolutionary pathway in which long-lived magma oceans drive the atmospheric"
        " diversity we observe among super-Earths."
    ),
    "kimura-2026-water": (
        "When a young planet's magma ocean interacts with its atmosphere, it can produce"
        " water vapor by reacting hydrogen with oxygen from the rock. We find that this"
        " process runs out of available oxygen surprisingly quickly, setting an upper limit"
        " on how water-rich a sub-Neptune's atmosphere can become through magma chemistry"
        " alone. Sub-Neptunes with very water-rich atmospheres would therefore need"
        " additional water delivered later, for instance by icy impacts."
    ),
    "nicholls-2025-self-limited": (
        "Rocky exoplanets on tight orbits experience internal tidal heating, similar to how"
        " Jupiter's gravity keeps Io volcanically active. We discovered a self-regulating"
        " feedback: as tidal heating melts the mantle, the softened rock dissipates tidal"
        " energy less efficiently, capping the heating rate far below previous estimates."
        " Despite this self-limitation, tidal heating in the L 98-59 system can still"
        " sustain magma oceans for billions of years."
    ),
    "boer-2025-absence": (
        "The 'runaway greenhouse' concept defines the inner edge of the habitable zone:"
        " the distance from a star where a planet's oceans would boil away irreversibly."
        " We show that this thermal limit, derived from pure-steam atmosphere models,"
        " vanishes when we account for the complex chemistry of atmospheres above magma"
        " oceans. Whether a planet retains habitable conditions depends not just on how"
        " much starlight it receives, but on the composition and melting state of its"
        " interior."
    ),
    "nicholls-2025-convective": (
        "Models of lava planets typically assume their thick atmospheres transport heat"
        " upward through convection, similar to boiling water. We find that some lava world"
        " atmospheres develop deep layers where convection shuts down entirely, yet the"
        " planet can still maintain a permanent magma ocean. This matters for interpreting"
        " upcoming telescope observations, because the atmospheric structure and chemistry"
        " change dramatically when convection is absent."
    ),
    "nicholls-2024-magma": (
        "The chemistry of a young planet's magma ocean, specifically how oxidized or"
        " reduced it is, controls which gases enter the atmosphere and how quickly the"
        " surface solidifies. We systematically explored this across a wide range of"
        " chemical conditions and found that hydrogen-rich atmospheres produced under"
        " reducing conditions can trap enough heat to prevent a magma ocean from ever"
        " freezing. The planet's oxidation state thus acts as a chemical switch between"
        " permanent magma ocean worlds and planets that solidify within a million years."
    ),
    "cesario-2024-large": (
        "Young rocky planets glow brightly in infrared light while their surfaces are"
        " still molten, making them visible at much greater distances than cooled,"
        " habitable-zone planets. We assessed whether the proposed LIFE space telescope"
        " could detect these young, molten worlds and found it could spot Earth-sized"
        " protoplanets in nearby star-forming regions within minutes to hours of"
        " observation. Detecting planets in this early molten stage would reveal how"
        " secondary atmospheres first form on rocky worlds."
    ),
    "lichtenberg-2022-reduced": (
        "Impacts of chemically reduced meteorites onto the early Earth may have triggered"
        " the production of molecules relevant for the origin of life. We simulated"
        " late-stage planet formation around stars of different masses and found that"
        " planets orbiting small M-dwarf stars receive far fewer of these reducing impacts."
        " This suggests that the chemical conditions thought to favor prebiotic chemistry"
        " are more likely around Sun-like stars than around the most common stars in the"
        " galaxy."
    ),
    "lichtenberg-2021-redox": (
        "When a super-Earth's interior is fully molten, iron droplets should sink to form"
        " a metal core, setting the oxidation state of the mantle. We show that turbulent"
        " convection in deep magma oceans can keep iron droplets suspended, preventing"
        " complete core formation and preserving a chemical memory of how the planet"
        " formed. This means two super-Earths of identical mass could have very different"
        " mantle and atmospheric compositions depending on their accretion history."
    ),
    "lichtenberg-2021-system-level": (
        "The relative abundances of water and carbon delivered to young planets depend on"
        " both the chemistry of the surrounding gas disk and the internal heating of the"
        " rocky building blocks. We show that radioactive heating inside planetesimals can"
        " drive off volatiles on the same timescale as disk chemistry rearranges them,"
        " creating correlated carbon-to-water ratios across a planetary system. Future"
        " measurements of exoplanet atmospheres may thus reveal when and how quickly a"
        " planet's building blocks formed."
    ),
    "lichtenberg-2021-vertically": (
        "The first atmosphere of a rocky planet forms when its molten surface releases"
        " trapped gases. We built a coupled model that tracks how different atmospheric"
        " gases interact with a solidifying magma ocean and control the planet's cooling"
        " rate. Hydrogen-dominated atmospheres slow cooling by orders of magnitude compared"
        " to nitrogen or carbon monoxide, meaning the dominant outgassed species"
        " fundamentally determines a young planet's thermal evolution."
    ),
    "lichtenberg-2021-bifurcation": (
        "Meteorite evidence shows that the Solar System's building blocks formed in two"
        " distinct chemical reservoirs, but the origin of this split was unclear. We"
        " demonstrate that the inward migration of the snow line in the young Solar System"
        " triggered two separate bursts of planetesimal formation, sampling different"
        " regions of the disk. These two populations then evolved along divergent"
        " geophysical paths, naturally explaining the compositional divide between the"
        " inner and outer Solar System."
    ),
    "lichtenberg-2019-water": (
        "Radioactive aluminum-26, inherited from a nearby supernova, heated the Solar"
        " System's earliest rocky bodies and drove off their water before they could grow"
        " into planets. We show that planetary systems rich in aluminum-26, like ours,"
        " preferentially form dry, rocky worlds, while systems without it form water-rich"
        " ocean planets. This mechanism can explain why the TRAPPIST-1 planets have similar"
        " water contents despite orbiting at very different distances from their star."
    ),
    "lichtenberg-2019-magma": (
        "The earliest rocky bodies in the Solar System melted from the inside out due to"
        " radioactive heating, but it has been unclear how magma moved through their"
        " interiors. We find that the grain size of silicate minerals is the critical"
        " factor: coarse-grained material lets magma segregate and create chemically"
        " layered structures, while fine-grained material traps melt in place. This"
        " connects the mineral texture of meteorites to the internal evolution and"
        " differentiation of their parent bodies."
    ),
    "lichtenberg-2018-impact": (
        "Chondrules, millimeter-sized glassy beads found in most meteorites, formed in"
        " energetic events during the first million years of the Solar System, but their"
        " origin remains debated. We tested whether collisions between partially molten"
        " planetesimals could produce chondrules with the right chemistry and found that"
        " the precursor bodies must not have been fully melted. This constrains either the"
        " timing and size of early planetesimals or the efficiency of collisional"
        " destruction in the young Solar System."
    ),
    "lichtenberg-2016-isotopic": (
        "Short-lived radioactive isotopes like aluminum-26 heated the building blocks of"
        " our Solar System and drove their internal evolution, but it is unclear how common"
        " such enrichment is elsewhere. We simulated the dispersal of supernova ejecta"
        " through young star clusters and found that the likelihood of Solar-System-level"
        " enrichment varies widely depending on the cluster's size and structure. Many"
        " planetary systems may receive even higher doses, implying that planetesimal"
        " evolution could differ substantially across the galaxy."
    ),
    "lichtenberg-2016-effects": (
        "The porous, powdery texture of freshly formed planetesimals acts as thermal"
        " insulation, potentially trapping radioactive heat and promoting internal melting."
        " We modeled how porosity and radioactive heating interact in 2D and 3D simulations"
        " and found that while porosity lowers the melting threshold, the size and formation"
        " time of a planetesimal are far more important in determining whether it"
        " differentiates. These results constrain which meteorite parent bodies underwent"
        " internal melting and how they contributed to terrestrial planet formation."
    ),
    "lichtenberg-2015-modeling": (
        "Giant planets might form rapidly when protoplanetary disks become gravitationally"
        " unstable and fragment into clumps, but capturing this process in simulations is"
        " numerically challenging. We developed a new 3D setup using adaptive mesh"
        " refinement to resolve the fragmentation of self-gravitating disks, identifying a"
        " minimum resolution requirement for reliably resolving gravitational collapse."
        " The resulting clumps migrate inward and are tidally destroyed, indicating that"
        " additional physics such as radiative feedback is needed to stabilize them into"
        " surviving planets."
    ),
    "lichtenberg-2025-constraining": (
        "Rocky exoplanets come in a wider range of sizes and compositions than anything in"
        " our Solar System, from bare rocky surfaces to gas-enveloped sub-Neptunes. This"
        " review synthesizes what atmospheric observations, particularly from JWST, are"
        " revealing about the geological processes shaping these worlds. It identifies the"
        " observational, experimental, and theoretical advances needed to eventually"
        " characterize truly Earth-like exoplanets."
    ),
    "lichtenberg-2025-super-earths": (
        "Astronomical surveys are now detecting rocky exoplanets small enough to be"
        " compared with Earth, but their compositions and climates challenge existing"
        " planetary science frameworks. This review covers what we know about super-Earths"
        " and Earth-like exoplanets, from their formation through magma ocean stages to"
        " their present-day atmospheres. Characterizing temperate, potentially habitable"
        " worlds will ultimately require space-based direct imaging missions capable of"
        " resolving their atmospheric composition."
    ),
    "lichtenberg-2023-geophysical": (
        "Understanding rocky planets requires connecting astrophysical disk processes to"
        " geophysical interior evolution, but these fields have traditionally been studied"
        " separately. This review traces how core, mantle, and atmosphere co-evolve during"
        " planetary formation, and how early divergences in thermal and chemical state"
        " determine whether a planet ends up habitable. Extending planetary science to"
        " exoplanets will demand advances in laboratory measurements and time-resolved"
        " theoretical models."
    ),
    "nicholls-2025-agni": (
        "Modeling the atmospheres of rocky exoplanets requires accurate calculations of"
        " how radiation and convection transport energy, especially for planets with molten"
        " surfaces. AGNI is an open-source atmospheric model purpose-built for lava worlds"
        " that uses an efficient numerical solver to calculate temperature profiles and"
        " radiation environments. It is designed to couple with interior evolution models"
        " within the PROTEUS simulation framework, enabling self-consistent simulations of"
        " how rocky planets evolve over time."
    ),
}


def main():
    with open(YAML_PATH) as f:
        pubs = yaml.safe_load(f)

    updated = 0
    for p in pubs:
        slug = p["slug"]
        if slug in DRAFTS and not p.get("lay_summary_draft"):
            p["lay_summary_draft"] = DRAFTS[slug]
            updated += 1

    with open(YAML_PATH, "w") as f:
        yaml.dump(pubs, f, default_flow_style=False, allow_unicode=True,
                  width=120, sort_keys=False)

    print(f"Updated {updated} entries with lay summary drafts.")


if __name__ == "__main__":
    main()
