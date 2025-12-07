"""
GenParamGetter - Generation Parameter Getter for SuperMerger

This module captures txt2img/img2img generation parameters from the Gradio UI
and sets up click handlers for SuperMerger's merge buttons.

Architecture:
-------------
1. GenParamGetter.after_component() - Finds txt2img/img2img generate buttons
2. GenParamGetter.get_params_components() - Called on app_started:
   - Extracts generation parameter components from Gradio dependencies
   - Stores them in components.txt2img_params / components.img2img_params
   - Calls _setup_click_events() to wire up merge button handlers

API Mode Compatibility:
-----------------------
When running with --api flag, the UI components don't exist. This module
handles this gracefully by:
- Checking if generate buttons were found before proceeding
- Skipping event setup if no valid dependencies found
- Using try/except blocks around component access

Click Event Handlers:
---------------------
_setup_click_events() wires up these buttons:
- merge, merge2: Merge models only
- mergeandgen, mergeandgen2: Merge and generate image
- gen, gen2: Generate image only
- s_reserve, s_reserve1: Reserve for XY plot
- gengrid: Generate XY grid
- s_startreserve: Start reserved XY plot
- rand_merge: Random merge

Note: frompromptb ("Get from prompt") is handled separately in supermerger.py
using JavaScript DOM injection for better reliability.
"""

import gradio as gr
import scripts.mergers.components as components
from scripts.mergers.mergers import smergegen, simggen
from scripts.mergers.xyplot import numanager

try:
    from scripts.mergers.pluslora import frompromptf
except ImportError as e:
    try:
        import transformers
        transformers_version = transformers.__version__
    except ImportError:
        transformers_version = "not installed"

    try:
        import diffusers
        diffusers_version = diffusers.__version__
    except ImportError:
        diffusers_version = "not installed"

    print(
        f"Version error: Failed to import module.\n"
        f"Transformers version: {transformers_version}\n"
        f"Diffusers version: {diffusers_version}\n"
        "Please ensure compatibility between these packages."
    )
    raise e

from modules import scripts, script_callbacks


class GenParamGetter(scripts.Script):
    """
    Script that captures generation parameters from txt2img/img2img tabs.
    """
    txt2img_gen_button = None
    img2img_gen_button = None
    events_assigned = False

    def title(self):
        return "Super Merger Generation Parameter Getter"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def after_component(self, component: gr.components.Component, **_kwargs):
        """Find generate buttons during component scan."""
        if component.elem_id == "txt2img_generate":
            GenParamGetter.txt2img_gen_button = component
        elif component.elem_id == "img2img_generate":
            GenParamGetter.img2img_gen_button = component

    @staticmethod
    def get_components_by_ids(root: gr.Blocks, ids: list[int]):
        """Recursively find Gradio components by their internal IDs."""
        found: list[gr.Blocks] = []
        if root._id in ids:
            found.append(root)
            ids = [_id for _id in ids if _id != root._id]
        if hasattr(root, "children"):
            for block in root.children:
                found.extend(GenParamGetter.get_components_by_ids(block, ids))
        return found

    @staticmethod
    def compare_components_with_ids(comps: list[gr.Blocks], ids: list[int]):
        """Check if a list of components matches a list of IDs."""
        try:
            return len(comps) == len(ids) and all(c._id == i for c, i in zip(comps, ids))
        except:
            return False

    @staticmethod
    def get_params_components(demo: gr.Blocks, app):
        """Extract generation parameter components from Gradio app."""
        if GenParamGetter.txt2img_gen_button is None or GenParamGetter.img2img_gen_button is None:
            print("GenParamsGetter: Generate buttons not found (--api mode?)")
            return

        for _id, _is_txt2img in zip(
            [GenParamGetter.txt2img_gen_button._id, GenParamGetter.img2img_gen_button._id],
            [True, False]
        ):
            tab = 'txt2img' if _is_txt2img else 'img2img'
            
            if hasattr(demo, "dependencies"):
                deps = [x for x in demo.dependencies if _id in x["targets"] and x.get("trigger") == "click"]
                g4 = False
            else:
                deps = [x for x in demo.config["dependencies"] if x["targets"][0][1] == "click" and _id in x["targets"][0]]
                g4 = True

            dep = next((d for d in deps if len(d["outputs"]) == 4), None)
            if dep is None:
                print(f"GenParamsGetter: No dependency for {tab}")
                continue

            try:
                if g4:
                    params = [demo.blocks[x] for x in dep['inputs']]
                else:
                    matching = [p for p in demo.fns if GenParamGetter.compare_components_with_ids(p.inputs, dep["inputs"])]
                    if not matching:
                        continue
                    params = matching[0].inputs

                if _is_txt2img:
                    components.txt2img_params = params
                else:
                    components.img2img_params = params
            except Exception as e:
                print(f"GenParamsGetter: Error for {tab}: {e}")

        if not GenParamGetter.events_assigned and components.txt2img_params:
            try:
                with demo:
                    _setup_click_events()
                GenParamGetter.events_assigned = True
            except Exception as e:
                print(f"GenParamsGetter: Error assigning events: {e}")


def _setup_click_events():
    """Set up click event handlers for SuperMerger buttons."""
    
    # === MERGE BUTTONS (Main Tab) ===
    components.merge.click(
        fn=smergegen,
        inputs=[*components.msettings, components.esettings1, *components.genparams,
                *components.hiresfix, *components.lucks, components.currentmodel,
                components.dfalse, *components.txt2img_params],
        outputs=[components.submit_result, components.currentmodel]
    )

    components.mergeandgen.click(
        fn=smergegen,
        inputs=[*components.msettings, components.esettings1, *components.genparams,
                *components.hiresfix, *components.lucks, components.currentmodel,
                components.dtrue, *components.txt2img_params],
        outputs=[components.submit_result, components.currentmodel, *components.imagegal]
    )

    components.gen.click(
        fn=simggen,
        inputs=[*components.genparams, *components.hiresfix, components.currentmodel,
                components.id_sets, gr.Textbox(value="No id", visible=False),
                *components.txt2img_params],
        outputs=[*components.imagegal]
    )

    # === MERGE BUTTONS (Duplicate Tab) ===
    components.merge2.click(
        fn=smergegen,
        inputs=[*components.msettings, components.esettings1, *components.genparams,
                *components.hiresfix, *components.lucks, components.currentmodel,
                components.dfalse, *components.txt2img_params],
        outputs=[components.submit_result, components.currentmodel]
    )

    components.mergeandgen2.click(
        fn=smergegen,
        inputs=[*components.msettings, components.esettings1, *components.genparams,
                *components.hiresfix, *components.lucks, components.currentmodel,
                components.dtrue, *components.txt2img_params],
        outputs=[components.submit_result, components.currentmodel, *components.imagegal]
    )

    components.gen2.click(
        fn=simggen,
        inputs=[*components.genparams, *components.hiresfix, components.currentmodel,
                components.id_sets, gr.Textbox(value="No id", visible=False),
                *components.txt2img_params],
        outputs=[*components.imagegal]
    )

    # === XY PLOT BUTTONS ===
    components.s_reserve.click(
        fn=numanager,
        inputs=[gr.Textbox(value="reserve", visible=False), *components.xysettings,
                *components.msettings, *components.genparams, *components.hiresfix,
                *components.lucks, *components.txt2img_params],
        outputs=[components.numaframe]
    )

    components.s_reserve1.click(
        fn=numanager,
        inputs=[gr.Textbox(value="reserve", visible=False), *components.xysettings,
                *components.msettings, *components.genparams, *components.hiresfix,
                *components.lucks, *components.txt2img_params],
        outputs=[components.numaframe]
    )

    components.gengrid.click(
        fn=numanager,
        inputs=[gr.Textbox(value="normal", visible=False), *components.xysettings,
                *components.msettings, *components.genparams, *components.hiresfix,
                *components.lucks, *components.txt2img_params],
        outputs=[components.submit_result, components.currentmodel, *components.imagegal]
    )

    components.s_startreserve.click(
        fn=numanager,
        inputs=[gr.Textbox(value=" ", visible=False), *components.xysettings,
                *components.msettings, *components.genparams, *components.hiresfix,
                *components.lucks, *components.txt2img_params],
        outputs=[components.submit_result, components.currentmodel, *components.imagegal]
    )

    components.rand_merge.click(
        fn=numanager,
        inputs=[gr.Textbox(value="random", visible=False), *components.xysettings,
                *components.msettings, *components.genparams, *components.hiresfix,
                *components.lucks, *components.txt2img_params],
        outputs=[components.submit_result, components.currentmodel, *components.imagegal]
    )


script_callbacks.on_app_started(GenParamGetter.get_params_components)