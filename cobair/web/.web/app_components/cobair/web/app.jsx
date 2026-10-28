
import {ReflexEvent,applyEventActions,isNotNullOrUndefined,isTrue,mergeSlotProps,pyAnd,refs} from "$/utils/state"
import {Fragment,memo,useCallback,useContext,useEffect,useRef} from "react"
import {Button as RadixThemesButton,Card as RadixThemesCard,Dialog as RadixThemesDialog,Flex as RadixThemesFlex,Heading as RadixThemesHeading,IconButton as RadixThemesIconButton,Select as RadixThemesSelect,Table as RadixThemesTable,Tabs as RadixThemesTabs,Text as RadixThemesText,TextField as RadixThemesTextField} from "@radix-ui/themes"
import {ClientSide,StateContexts,addEvents} from "$/utils/context"
import {jsx} from "@emotion/react"
import {} from "react-dropzone"
import {useDropzone} from "react-dropzone"
import LucideUpload from "lucide-react/dist/esm/icons/upload.mjs"
import LucidePencil from "lucide-react/dist/esm/icons/pencil.mjs"
import LucideTrash2 from "lucide-react/dist/esm/icons/trash-2.mjs"
import LucideX from "lucide-react/dist/esm/icons/x.mjs"
import {ReactFlow} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import {Bar as RechartsBar,CartesianGrid as RechartsCartesianGrid,Cell as RechartsCell,ReferenceLine as RechartsReferenceLine,ResponsiveContainer as RechartsResponsiveContainer,Tooltip as RechartsTooltip,XAxis as RechartsXAxis,YAxis as RechartsYAxis} from "recharts"
import DebounceInput from "react-debounce-input"

const RechartsBarChart = ClientSide(() => import('recharts').then((mod) => mod.BarChart), "RechartsBarChart")






export const Button_button_85c22a3e424fd84f9ad05fd8fb631097_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_85c22a3e424fd84f9ad05fd8fb631097_85ab63b1 = memo(({children, ...rest}) => {
    const ref_new_config = useRef(null); refs["ref_new_config"] = ref_new_config;
const on_click_f7487adbeda81d4be8f4f5b46fb4c8f9 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.new_config", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"new-config", onClick:on_click_f7487adbeda81d4be8f4f5b46fb4c8f9, ref:ref_new_config, variant:"soft" }))},children)
    )
});
Button_button_85c22a3e424fd84f9ad05fd8fb631097_85ab63b1.displayName = "Button";
return Button_button_85c22a3e424fd84f9ad05fd8fb631097_85ab63b1;
})();

export const Upload_comp_7a4e2f6713711b29ea4e8ca8397fa6a8_85ab63b1 = /*#__PURE__*/ (() => {
const Upload_comp_7a4e2f6713711b29ea4e8ca8397fa6a8_85ab63b1 = memo(({children}) => {
    const ref_config_upload = useRef(null); refs["ref_config_upload"] = ref_config_upload;
const on_drop_6c3b8518b58818122a6ddb68796b2bcf = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.upload_config", ({ ["files"] : _ev_0, ["upload_param_name"] : "files", ["upload_id"] : "config_upload", ["extra_headers"] : ({  }) }), ({  }), "uploadFiles"))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const on_drop_rejected_2fcedbdc0771e7617b4270e2d1ac8cc9 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("_call_function", ({ ["function"] : (() => (refs['__toast']?.["error"]("", ({ ["title"] : "Files not Accepted", ["description"] : _ev_0.map(((osizayzf) => (osizayzf?.["file"]?.["path"]+": "+osizayzf?.["errors"].map(((wnkiegyk) => wnkiegyk?.["message"])).join(", ")))).join("\n\n"), ["closeButton"] : true, ["style"] : ({ ["whiteSpace"] : "pre-line" }) })))), ["callback"] : null }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const { getRootProps: xdvxrcsn, getInputProps: udaxihhe, isDragActive: bacghqta} = useDropzone(({ ["accept"] : ({ ["application/x-yaml"] : [".yml", ".yaml"], ["text/yaml"] : [".yml", ".yaml"] }), ["multiple"] : false, ["maxFiles"] : 1, ["onDrop"] : on_drop_6c3b8518b58818122a6ddb68796b2bcf, ["id"] : "config_upload", ["onDropRejected"] : on_drop_rejected_2fcedbdc0771e7617b4270e2d1ac8cc9 }));
const ref_load_yaml = useRef(null); refs["ref_load_yaml"] = ref_load_yaml;



    return(
        jsx(Fragment,{},jsx("div",{className:"rx-Upload",id:"config_upload",ref:ref_config_upload,...xdvxrcsn()},jsx("input",{type:"file",...udaxihhe()},),jsx(RadixThemesButton,{id:"load-yaml",ref:ref_load_yaml,variant:"soft"},jsx(LucideUpload,{size:16},),"Load YAML")))
    )
});
Upload_comp_7a4e2f6713711b29ea4e8ca8397fa6a8_85ab63b1.displayName = "Upload";
return Upload_comp_7a4e2f6713711b29ea4e8ca8397fa6a8_85ab63b1;
})();

export const Button_button_9d4f7839321f717967c363cf19243ed5_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_9d4f7839321f717967c363cf19243ed5_85ab63b1 = memo(({children, ...rest}) => {
    const ref_load_example = useRef(null); refs["ref_load_example"] = ref_load_example;
const on_click_d66ec5be9faa9a518047d4248bb2a39e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.load_example", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"load-example", onClick:on_click_d66ec5be9faa9a518047d4248bb2a39e, ref:ref_load_example, variant:"soft" }))},children)
    )
});
Button_button_9d4f7839321f717967c363cf19243ed5_85ab63b1.displayName = "Button";
return Button_button_9d4f7839321f717967c363cf19243ed5_85ab63b1;
})();

export const Button_button_190f969d6f2b388199889ec9a619a1d2_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_190f969d6f2b388199889ec9a619a1d2_85ab63b1 = memo(({children, ...rest}) => {
    const ref_download = useRef(null); refs["ref_download"] = ref_download;
const on_click_c901a2d76450bd97d988e7891e3dbfea = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.download_config", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"download", onClick:on_click_c901a2d76450bd97d988e7891e3dbfea, ref:ref_download, variant:"soft" }))},children)
    )
});
Button_button_190f969d6f2b388199889ec9a619a1d2_85ab63b1.displayName = "Button";
return Button_button_190f969d6f2b388199889ec9a619a1d2_85ab63b1;
})();

export const Button_button_e3a3126dc7a6ab2b867e95bc08e16150_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_e3a3126dc7a6ab2b867e95bc08e16150_85ab63b1 = memo(({children, ...rest}) => {
    const ref_save = useRef(null); refs["ref_save"] = ref_save;
const on_click_7ddb81906602c654b9662aa96a0ae60e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.save_config", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"save", onClick:on_click_7ddb81906602c654b9662aa96a0ae60e, ref:ref_save }))},children)
    )
});
Button_button_e3a3126dc7a6ab2b867e95bc08e16150_85ab63b1.displayName = "Button";
return Button_button_e3a3126dc7a6ab2b867e95bc08e16150_85ab63b1;
})();

export const Cond_comp_0991d4e84229ad9693c1da59f5831ea1_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_0991d4e84229ad9693c1da59f5831ea1_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.local_file_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_0991d4e84229ad9693c1da59f5831ea1_85ab63b1.displayName = "Cond";
return Cond_comp_0991d4e84229ad9693c1da59f5831ea1_85ab63b1;
})();

export const Iconbutton_iconbutton_c732e05f5c7f0028480ec0c72da57f3d_85ab63b1 = /*#__PURE__*/ (() => {
const Iconbutton_iconbutton_c732e05f5c7f0028480ec0c72da57f3d_85ab63b1 = memo(({children, ...rest}) => {
    const ref_undo = useRef(null); refs["ref_undo"] = ref_undo;
const on_click_803cd2ac7c0dd157a6f287757ac04fc8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.undo", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesIconButton,{...mergeSlotProps(rest, ({ "aria-label":"Undo", css:({ ["padding"] : "6px" }), disabled:!(reflex___state____state__cobair___web___state____editor_state.can_undo_rx_state_), id:"undo", onClick:on_click_803cd2ac7c0dd157a6f287757ac04fc8, ref:ref_undo, variant:"soft" }))},children)
    )
});
Iconbutton_iconbutton_c732e05f5c7f0028480ec0c72da57f3d_85ab63b1.displayName = "IconButton";
return Iconbutton_iconbutton_c732e05f5c7f0028480ec0c72da57f3d_85ab63b1;
})();

export const Iconbutton_iconbutton_77f1112f4403647cb7a768607ba0f4d6_85ab63b1 = /*#__PURE__*/ (() => {
const Iconbutton_iconbutton_77f1112f4403647cb7a768607ba0f4d6_85ab63b1 = memo(({children, ...rest}) => {
    const ref_redo = useRef(null); refs["ref_redo"] = ref_redo;
const on_click_bf40eb35237cb4aab5a4bd2d33a779d0 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.redo", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesIconButton,{...mergeSlotProps(rest, ({ "aria-label":"Redo", css:({ ["padding"] : "6px" }), disabled:!(reflex___state____state__cobair___web___state____editor_state.can_redo_rx_state_), id:"redo", onClick:on_click_bf40eb35237cb4aab5a4bd2d33a779d0, ref:ref_redo, variant:"soft" }))},children)
    )
});
Iconbutton_iconbutton_77f1112f4403647cb7a768607ba0f4d6_85ab63b1.displayName = "IconButton";
return Iconbutton_iconbutton_77f1112f4403647cb7a768607ba0f4d6_85ab63b1;
})();

export const Bare_comp_eaeba7f72fb720b39e587f38628bdd62_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_eaeba7f72fb720b39e587f38628bdd62_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.file_name_rx_state_
    )
});
Bare_comp_eaeba7f72fb720b39e587f38628bdd62_85ab63b1.displayName = "Bare";
return Bare_comp_eaeba7f72fb720b39e587f38628bdd62_85ab63b1;
})();

export const Cond_comp_cc5d2e4d2cc0318536568b2a83ac2e76_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_cc5d2e4d2cc0318536568b2a83ac2e76_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.file_name_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_cc5d2e4d2cc0318536568b2a83ac2e76_85ab63b1.displayName = "Cond";
return Cond_comp_cc5d2e4d2cc0318536568b2a83ac2e76_85ab63b1;
})();

export const Cond_comp_7d9f0eeb39feabf4b7b347dc5cf6afe3_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_7d9f0eeb39feabf4b7b347dc5cf6afe3_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (reflex___state____state__cobair___web___state____editor_state.dirty_rx_state_?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_7d9f0eeb39feabf4b7b347dc5cf6afe3_85ab63b1.displayName = "Cond";
return Cond_comp_7d9f0eeb39feabf4b7b347dc5cf6afe3_85ab63b1;
})();

export const Bare_comp_74f8ee7b51a7802d8700bc5e0344e83a_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_74f8ee7b51a7802d8700bc5e0344e83a_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.error_rx_state_
    )
});
Bare_comp_74f8ee7b51a7802d8700bc5e0344e83a_85ab63b1.displayName = "Bare";
return Bare_comp_74f8ee7b51a7802d8700bc5e0344e83a_85ab63b1;
})();

export const Cond_comp_83c16423e00e6bc59a74e9ca0212c3bc_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_83c16423e00e6bc59a74e9ca0212c3bc_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.error_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_83c16423e00e6bc59a74e9ca0212c3bc_85ab63b1.displayName = "Cond";
return Cond_comp_83c16423e00e6bc59a74e9ca0212c3bc_85ab63b1;
})();

export const Bare_comp_7e5879eb31c820d933a941e70b94d043_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_7e5879eb31c820d933a941e70b94d043_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.info_rx_state_
    )
});
Bare_comp_7e5879eb31c820d933a941e70b94d043_85ab63b1.displayName = "Bare";
return Bare_comp_7e5879eb31c820d933a941e70b94d043_85ab63b1;
})();

export const Cond_comp_f4ac22fb4541c0c82479b92e38d0adc7_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_f4ac22fb4541c0c82479b92e38d0adc7_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.info_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_f4ac22fb4541c0c82479b92e38d0adc7_85ab63b1.displayName = "Cond";
return Cond_comp_f4ac22fb4541c0c82479b92e38d0adc7_85ab63b1;
})();

export const Foreach_comp_365992c9b066f9ce46cb46e525914650_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_365992c9b066f9ce46cb46e525914650_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.problems_rx_state_ ?? [],((children_rx_state_,props_rx_state_)=>(jsx(RadixThemesText,{as:"p",key:props_rx_state_},children_rx_state_))))
    )
});
Foreach_comp_365992c9b066f9ce46cb46e525914650_85ab63b1.displayName = "Foreach";
return Foreach_comp_365992c9b066f9ce46cb46e525914650_85ab63b1;
})();

export const Cond_comp_f0097052dac8df08b64a7703f97041f6_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_f0097052dac8df08b64a7703f97041f6_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        ((reflex___state____state__cobair___web___state____editor_state.contexts_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_f0097052dac8df08b64a7703f97041f6_85ab63b1.displayName = "Cond";
return Cond_comp_f0097052dac8df08b64a7703f97041f6_85ab63b1;
})();

export const Cond_comp_2866455f090770d0ab487919d8ef76a2_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_2866455f090770d0ab487919d8ef76a2_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        ((reflex___state____state__cobair___web___state____editor_state.problems_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_2866455f090770d0ab487919d8ef76a2_85ab63b1.displayName = "Cond";
return Cond_comp_2866455f090770d0ab487919d8ef76a2_85ab63b1;
})();

export const Reactflow_reactflow_dc949a01c0b288c59f65accbb2b225ce_85ab63b1 = /*#__PURE__*/ (() => {
const Reactflow_reactflow_dc949a01c0b288c59f65accbb2b225ce_85ab63b1 = memo(({children, ...rest}) => {
    const on_node_click_5e890149c97f85b4b4c2d07e51e4cb69 = useCallback(((__event, _item) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.graph_node_click", ({ ["node_id"] : _item?.["id"] }), ({  })))], [__event, _item], ({  })))), [addEvents, ReflexEvent])
const on_edge_click_ba0e223f1555997a95406ef0fa0a06e2 = useCallback(((__event, _item) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.graph_edge_click", ({ ["edge_id"] : _item?.["id"] }), ({  })))], [__event, _item], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(ReactFlow,{...mergeSlotProps(rest, ({ edges:reflex___state____state__cobair___web___state____editor_state.graph_edges_rx_state_, elementsSelectable:false, fitView:true, key:reflex___state____state__cobair___web___state____editor_state.graph_key_rx_state_, maxZoom:2.0, minZoom:0.2, nodes:reflex___state____state__cobair___web___state____editor_state.graph_nodes_rx_state_, nodesConnectable:false, nodesDraggable:false, onEdgeClick:on_edge_click_ba0e223f1555997a95406ef0fa0a06e2, onNodeClick:on_node_click_5e890149c97f85b4b4c2d07e51e4cb69, preventScrolling:false, zoomOnScroll:false }))},children)
    )
});
Reactflow_reactflow_dc949a01c0b288c59f65accbb2b225ce_85ab63b1.displayName = "ReactFlow";
return Reactflow_reactflow_dc949a01c0b288c59f65accbb2b225ce_85ab63b1;
})();

export const Cond_comp_e6736cd26fcd6b6da1238301de71097b_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_e6736cd26fcd6b6da1238301de71097b_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        ((reflex___state____state__cobair___web___state____editor_state.graph_nodes_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_e6736cd26fcd6b6da1238301de71097b_85ab63b1.displayName = "Cond";
return Cond_comp_e6736cd26fcd6b6da1238301de71097b_85ab63b1;
})();

export const Button_button_faf09e3a290cf277f518f74597d6bc40_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_faf09e3a290cf277f518f74597d6bc40_85ab63b1 = memo(({children, ...rest}) => {
    const ref_add_context = useRef(null); refs["ref_add_context"] = ref_add_context;
const on_click_4ccdffa04ca692b42bddb98298610604 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.open_new_context", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"add-context", onClick:on_click_4ccdffa04ca692b42bddb98298610604, ref:ref_add_context, size:"1", variant:"soft" }))},children)
    )
});
Button_button_faf09e3a290cf277f518f74597d6bc40_85ab63b1.displayName = "Button";
return Button_button_faf09e3a290cf277f518f74597d6bc40_85ab63b1;
})();

export const Foreach_comp_e3de689ebf77a2b09c83ea9f1f24a687_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_e3de689ebf77a2b09c83ea9f1f24a687_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.contexts_rx_state_ ?? [],((context_rx_state_,index_rx_state_)=>(jsx(RadixThemesCard,{className:"context-card",css:({ ["width"] : "100%" }),key:index_rx_state_},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesHeading,{className:"context-name",size:"3"},context_rx_state_?.["name"]),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesIconButton,{"aria-label":"Edit context",className:"edit-context",css:({ ["padding"] : "6px" }),onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.open_edit_context", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  })))),size:"1",variant:"ghost"},jsx(LucidePencil,{size:12},)),jsx(RadixThemesIconButton,{"aria-label":"Delete context",className:"delete-context",color:"red",css:({ ["padding"] : "6px" }),onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.delete_context", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  })))),size:"1",variant:"ghost"},jsx(LucideTrash2,{size:12},))),Array.prototype.map.call(context_rx_state_?.["instantiations"] ?? [],((instantiation_rx_state_,instantiation_index_rx_state_)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:instantiation_index_rx_state_,gap:"3"},jsx(RadixThemesText,{as:"p",css:({ ["width"] : "50%" })},instantiation_rx_state_?.["name"]),jsx(RadixThemesTextField.Root,{"aria-label":"Apriori probability",className:"apriori-input",css:({ ["width"] : "50%" }),defaultValue:instantiation_rx_state_?.["apriori"],key:(reflex___state____state__cobair___web___state____editor_state.revision_rx_state_+"-"+index_rx_state_+"-"+instantiation_index_rx_state_),onBlur:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_apriori", ({ ["context_index"] : index_rx_state_, ["instantiation_index"] : instantiation_index_rx_state_, ["text"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),size:"1"},)))))))))
    )
});
Foreach_comp_e3de689ebf77a2b09c83ea9f1f24a687_85ab63b1.displayName = "Foreach";
return Foreach_comp_e3de689ebf77a2b09c83ea9f1f24a687_85ab63b1;
})();

export const Button_button_92b4284abcf3cedb6502e0c96d80fdeb_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_92b4284abcf3cedb6502e0c96d80fdeb_85ab63b1 = memo(({children, ...rest}) => {
    const ref_add_intention = useRef(null); refs["ref_add_intention"] = ref_add_intention;
const on_click_6559e5afe782ca9c8704f06ac9d1e2f4 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.open_new_intention", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"add-intention", onClick:on_click_6559e5afe782ca9c8704f06ac9d1e2f4, ref:ref_add_intention, size:"1", variant:"soft" }))},children)
    )
});
Button_button_92b4284abcf3cedb6502e0c96d80fdeb_85ab63b1.displayName = "Button";
return Button_button_92b4284abcf3cedb6502e0c96d80fdeb_85ab63b1;
})();

export const Foreach_comp_5b64c549fdca38ae148ed5f8e36c700e_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_5b64c549fdca38ae148ed5f8e36c700e_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.intentions_rx_state_ ?? [],((intention_rx_state_,index_rx_state_)=>(jsx(RadixThemesCard,{className:"intention-card",css:({ ["width"] : "100%" }),key:index_rx_state_},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",gap:"3"},jsx(RadixThemesText,{as:"p",className:"intention-name"},intention_rx_state_),jsx(RadixThemesFlex,{css:({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })},),jsx(RadixThemesIconButton,{"aria-label":"Rename intention",className:"rename-intention",css:({ ["padding"] : "6px" }),onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.open_rename_intention", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  })))),size:"1",variant:"ghost"},jsx(LucidePencil,{size:12},)),jsx(RadixThemesIconButton,{"aria-label":"Delete intention",className:"delete-intention",color:"red",css:({ ["padding"] : "6px" }),onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.delete_intention", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  })))),size:"1",variant:"ghost"},jsx(LucideTrash2,{size:12},)))))))
    )
});
Foreach_comp_5b64c549fdca38ae148ed5f8e36c700e_85ab63b1.displayName = "Foreach";
return Foreach_comp_5b64c549fdca38ae148ed5f8e36c700e_85ab63b1;
})();

export const Foreach_comp_03341102612d3d1e6d60cbb1efd31c48_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_03341102612d3d1e6d60cbb1efd31c48_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.contexts_rx_state_ ?? [],((context_rx_state_,index_rx_state_)=>(jsx(RadixThemesSelect.Item,{key:index_rx_state_,value:(JSON.stringify(index_rx_state_))},context_rx_state_?.["name"]))))
    )
});
Foreach_comp_03341102612d3d1e6d60cbb1efd31c48_85ab63b1.displayName = "Foreach";
return Foreach_comp_03341102612d3d1e6d60cbb1efd31c48_85ab63b1;
})();

export const Selectroot_select__root_eab798581c2609328234930a31c2d267_85ab63b1 = /*#__PURE__*/ (() => {
const Selectroot_select__root_eab798581c2609328234930a31c2d267_85ab63b1 = memo(({children, ...rest}) => {
    const on_change_4acc8ff8efa462fa80e7fbd99653df83 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.select_influence_context", ({ ["index"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_4acc8ff8efa462fa80e7fbd99653df83, value:reflex___state____state__cobair___web___state____editor_state.influence_context_rx_state_ }))},children)
    )
});
Selectroot_select__root_eab798581c2609328234930a31c2d267_85ab63b1.displayName = "SelectRoot";
return Selectroot_select__root_eab798581c2609328234930a31c2d267_85ab63b1;
})();

export const Foreach_comp_100f056139bc90f74cd4ac24e39e5f20_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_100f056139bc90f74cd4ac24e39e5f20_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.intentions_rx_state_ ?? [],((intention_rx_state_,index_rx_state_)=>(jsx(RadixThemesTable.ColumnHeaderCell,{className:"intention-column",css:({ ["color"] : ((index_rx_state_?.valueOf?.() === reflex___state____state__cobair___web___state____editor_state.selected_intention_rx_state_?.valueOf?.()) ? "var(--accent-11)" : "inherit") }),key:index_rx_state_},intention_rx_state_))))
    )
});
Foreach_comp_100f056139bc90f74cd4ac24e39e5f20_85ab63b1.displayName = "Foreach";
return Foreach_comp_100f056139bc90f74cd4ac24e39e5f20_85ab63b1;
})();

export const Foreach_comp_c56f6856fee447aff6199fd07eee1c84_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_c56f6856fee447aff6199fd07eee1c84_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.influence_rows_rx_state_ ?? [],((row_rx_state_,instantiation_index_rx_state_)=>(jsx(RadixThemesTable.Row,{key:instantiation_index_rx_state_},jsx(RadixThemesTable.RowHeaderCell,{},row_rx_state_?.["name"]),Array.prototype.map.call(row_rx_state_?.["influences"] ?? [],((value_rx_state_,intention_index_rx_state_)=>(jsx(RadixThemesTable.Cell,{key:intention_index_rx_state_},jsx(RadixThemesSelect.Root,{onValueChange:((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_influence", ({ ["instantiation_index"] : instantiation_index_rx_state_, ["intention_index"] : intention_index_rx_state_, ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))),size:"1",value:value_rx_state_},jsx(RadixThemesSelect.Trigger,{className:"influence-select",css:({ ["width"] : "100%" })},),jsx(RadixThemesSelect.Content,{},jsx(RadixThemesSelect.Item,{value:"0"},"0 - not probable (0%)"),jsx(RadixThemesSelect.Item,{value:"1"},"1 - not very probable (5%)"),jsx(RadixThemesSelect.Item,{value:"2"},"2 - somewhat probable (25%)"),jsx(RadixThemesSelect.Item,{value:"3"},"3 - even probability (50%)"),jsx(RadixThemesSelect.Item,{value:"4"},"4 - very probable (75%)"),jsx(RadixThemesSelect.Item,{value:"5"},"5 - definitely probable (95%)")))))))))))
    )
});
Foreach_comp_c56f6856fee447aff6199fd07eee1c84_85ab63b1.displayName = "Foreach";
return Foreach_comp_c56f6856fee447aff6199fd07eee1c84_85ab63b1;
})();

export const Cond_comp_95de0a7331f77c5e072a490a634eab38_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_95de0a7331f77c5e072a490a634eab38_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (pyAnd((reflex___state____state__cobair___web___state____editor_state.contexts_rx_state_.length > 0), () => ((reflex___state____state__cobair___web___state____editor_state.intentions_rx_state_.length > 0)))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_95de0a7331f77c5e072a490a634eab38_85ab63b1.displayName = "Cond";
return Cond_comp_95de0a7331f77c5e072a490a634eab38_85ab63b1;
})();

export const Button_button_a1a8aed5ee92558776f3ecb234166ba2_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_a1a8aed5ee92558776f3ecb234166ba2_85ab63b1 = memo(({children, ...rest}) => {
    const ref_add_combined = useRef(null); refs["ref_add_combined"] = ref_add_combined;
const on_click_865405e125a0b28d68dc5a68b152ca1b = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.open_combined_dialog", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"add-combined", onClick:on_click_865405e125a0b28d68dc5a68b152ca1b, ref:ref_add_combined, size:"1", variant:"soft" }))},children)
    )
});
Button_button_a1a8aed5ee92558776f3ecb234166ba2_85ab63b1.displayName = "Button";
return Button_button_a1a8aed5ee92558776f3ecb234166ba2_85ab63b1;
})();

export const Foreach_comp_173c254c59733dfe0c0781b2b381e87c_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_173c254c59733dfe0c0781b2b381e87c_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.combined_rx_state_ ?? [],((combined_rx_state_,index_rx_state_)=>(jsx(RadixThemesTable.Row,{className:"combined-row",key:index_rx_state_},jsx(RadixThemesTable.Cell,{},combined_rx_state_?.["intention"]),jsx(RadixThemesTable.Cell,{},combined_rx_state_?.["combination"]),jsx(RadixThemesTable.Cell,{},combined_rx_state_?.["value"]),jsx(RadixThemesTable.Cell,{},jsx(RadixThemesIconButton,{"aria-label":"Remove",className:"remove-combined",color:"red",css:({ ["padding"] : "6px" }),onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.remove_combined", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  })))),size:"1",variant:"ghost"},jsx(LucideTrash2,{size:12},)))))))
    )
});
Foreach_comp_173c254c59733dfe0c0781b2b381e87c_85ab63b1.displayName = "Foreach";
return Foreach_comp_173c254c59733dfe0c0781b2b381e87c_85ab63b1;
})();

export const Cond_comp_cbf6533e45699b4bccc6a63c050f5be7_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_cbf6533e45699b4bccc6a63c050f5be7_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        ((reflex___state____state__cobair___web___state____editor_state.combined_rx_state_.length > 0)?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_cbf6533e45699b4bccc6a63c050f5be7_85ab63b1.displayName = "Cond";
return Cond_comp_cbf6533e45699b4bccc6a63c050f5be7_85ab63b1;
})();

export const Textfieldroot_textfield__root_70126634871b94e1e823562c95c66c9b_85ab63b1 = /*#__PURE__*/ (() => {
const Textfieldroot_textfield__root_70126634871b94e1e823562c95c66c9b_85ab63b1 = memo(({children, ...rest}) => {
    const ref_threshold = useRef(null); refs["ref_threshold"] = ref_threshold;
const on_blur_a8b2caf84e21ad39e1459ca83067ac70 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_threshold", ({ ["text"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesTextField.Root,{...mergeSlotProps(rest, ({ "aria-label":"Decision threshold", css:({ ["width"] : "10em" }), defaultValue:reflex___state____state__cobair___web___state____editor_state.decision_threshold_rx_state_, id:"threshold", key:(reflex___state____state__cobair___web___state____editor_state.revision_rx_state_+"-threshold"), onBlur:on_blur_a8b2caf84e21ad39e1459ca83067ac70, ref:ref_threshold }))},)
    )
});
Textfieldroot_textfield__root_70126634871b94e1e823562c95c66c9b_85ab63b1.displayName = "TextFieldRoot";
return Textfieldroot_textfield__root_70126634871b94e1e823562c95c66c9b_85ab63b1;
})();

export const Bare_comp_c28457df0fd5c474c69cfe2559a02f40_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_c28457df0fd5c474c69cfe2559a02f40_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.inference_error_rx_state_
    )
});
Bare_comp_c28457df0fd5c474c69cfe2559a02f40_85ab63b1.displayName = "Bare";
return Bare_comp_c28457df0fd5c474c69cfe2559a02f40_85ab63b1;
})();

export const Foreach_comp_591421a6216955c75bf25e5b1a8f472c_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_591421a6216955c75bf25e5b1a8f472c_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.contexts_rx_state_ ?? [],((context_rx_state_,index_rx_state_)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_rx_state_,gap:"3"},jsx(RadixThemesText,{as:"p",css:({ ["width"] : "45%" })},context_rx_state_?.["name"]),jsx(RadixThemesSelect.Root,{onValueChange:((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_evidence", ({ ["context_index"] : index_rx_state_, ["instantiation_index"] : _ev_0 }), ({  })))], [_ev_0], ({  })))),value:(JSON.stringify(reflex___state____state__cobair___web___state____editor_state.evidence_rx_state_?.at?.(index_rx_state_)))},jsx(RadixThemesSelect.Trigger,{className:"evidence-select",css:({ ["flex"] : "1" })},),jsx(RadixThemesSelect.Content,{},jsx(RadixThemesSelect.Item,{value:"-1"},"unknown"),Array.prototype.map.call(context_rx_state_?.["instantiations"] ?? [],((instantiation_rx_state_,instantiation_index_rx_state_)=>(jsx(RadixThemesSelect.Item,{key:instantiation_index_rx_state_,value:(JSON.stringify(instantiation_index_rx_state_))},instantiation_rx_state_?.["name"]))))))))))
    )
});
Foreach_comp_591421a6216955c75bf25e5b1a8f472c_85ab63b1.displayName = "Foreach";
return Foreach_comp_591421a6216955c75bf25e5b1a8f472c_85ab63b1;
})();

export const Button_button_39f57d1dafdee0991e5385dbe0889ecd_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_39f57d1dafdee0991e5385dbe0889ecd_85ab63b1 = memo(({children, ...rest}) => {
    const ref_reset_evidence = useRef(null); refs["ref_reset_evidence"] = ref_reset_evidence;
const on_click_0643db4002d4f3c41a2a0c18df97865e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.reset_evidence", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"reset-evidence", onClick:on_click_0643db4002d4f3c41a2a0c18df97865e, ref:ref_reset_evidence, size:"1", variant:"soft" }))},children)
    )
});
Button_button_39f57d1dafdee0991e5385dbe0889ecd_85ab63b1.displayName = "Button";
return Button_button_39f57d1dafdee0991e5385dbe0889ecd_85ab63b1;
})();

export const Bare_comp_8551fa97f33500f46a7c10343eb8cb3f_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_8551fa97f33500f46a7c10343eb8cb3f_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.recognized_rx_state_
    )
});
Bare_comp_8551fa97f33500f46a7c10343eb8cb3f_85ab63b1.displayName = "Bare";
return Bare_comp_8551fa97f33500f46a7c10343eb8cb3f_85ab63b1;
})();

export const Responsivecontainer_responsivecontainer_e73e71be857250d00f0cea4da31bb247_85ab63b1 = /*#__PURE__*/ (() => {
const Responsivecontainer_responsivecontainer_e73e71be857250d00f0cea4da31bb247_85ab63b1 = memo(({children, ...rest}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RechartsResponsiveContainer,{...mergeSlotProps(rest, ({ height:320, minHeight:10, minWidth:10, width:"100%" }))},jsx(RechartsBarChart,{data:reflex___state____state__cobair___web___state____editor_state.results_rx_state_,height:"100%",width:"100%"},jsx(RechartsCartesianGrid,{stroke:"var(--gray-7)",strokeDasharray:"3 3",vertical:false},),jsx(RechartsXAxis,{dataKey:"name",stroke:"var(--gray-9)"},),jsx(RechartsYAxis,{domain:[0, 100],stroke:"var(--gray-9)",unit:"%"},),jsx(RechartsTooltip,{contentStyle:({ ["background"] : "var(--gray-1)", ["borderColor"] : "var(--gray-4)", ["borderRadius"] : "8px" }),cursor:({ ["strokeWidth"] : 1, ["fill"] : "var(--gray-3)" }),itemStyle:({ ["color"] : "var(--gray-12)" }),labelStyle:({ ["color"] : "var(--gray-11)" })},),jsx(RechartsBar,{dataKey:"probability",fill:"var(--accent-9)",isAnimationActive:false,name:"Probability",unit:"%"},Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.results_rx_state_ ?? [],((result_rx_state_,index_b0bdf5ff32fec38642882cf594d79952)=>(jsx(RechartsCell,{fill:result_rx_state_?.["fill"],key:index_b0bdf5ff32fec38642882cf594d79952},))))),jsx(RechartsReferenceLine,{label:"decision threshold",stroke:"var(--red-9)",strokeDasharray:"6 4",y:(JSON.stringify(reflex___state____state__cobair___web___state____editor_state.threshold_percent_rx_state_))},)))
    )
});
Responsivecontainer_responsivecontainer_e73e71be857250d00f0cea4da31bb247_85ab63b1.displayName = "ResponsiveContainer";
return Responsivecontainer_responsivecontainer_e73e71be857250d00f0cea4da31bb247_85ab63b1;
})();

export const Cond_comp_6582c7c344e4577e3f82701ae89c69bc_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_6582c7c344e4577e3f82701ae89c69bc_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.inference_error_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_6582c7c344e4577e3f82701ae89c69bc_85ab63b1.displayName = "Cond";
return Cond_comp_6582c7c344e4577e3f82701ae89c69bc_85ab63b1;
})();

export const Tabsroot_tabs__root_28c2f67c73961db9a008fdbc1c088e9b_85ab63b1 = /*#__PURE__*/ (() => {
const Tabsroot_tabs__root_28c2f67c73961db9a008fdbc1c088e9b_85ab63b1 = memo(({children, ...rest}) => {
    const on_change_2501accd9c08d16bc3706443a07280e6 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_tab", ({ ["tab"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesTabs.Root,{...mergeSlotProps(rest, ({ css:({ ["&[data-orientation='vertical']"] : ({ ["display"] : "flex" }), ["width"] : "100%" }), onValueChange:on_change_2501accd9c08d16bc3706443a07280e6, value:reflex___state____state__cobair___web___state____editor_state.tab_rx_state_ }))},children)
    )
});
Tabsroot_tabs__root_28c2f67c73961db9a008fdbc1c088e9b_85ab63b1.displayName = "TabsRoot";
return Tabsroot_tabs__root_28c2f67c73961db9a008fdbc1c088e9b_85ab63b1;
})();

export const Bare_comp_8ee631ed648ab66fa3dbfed3470cc218_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_8ee631ed648ab66fa3dbfed3470cc218_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        ((reflex___state____state__cobair___web___state____editor_state.context_dialog_index_rx_state_ >= 0) ? "Edit context" : "New context")
    )
});
Bare_comp_8ee631ed648ab66fa3dbfed3470cc218_85ab63b1.displayName = "Bare";
return Bare_comp_8ee631ed648ab66fa3dbfed3470cc218_85ab63b1;
})();

export const Debounceinput_debounceinput_8cac14ffa7c449093068c59562534e1d_85ab63b1 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_8cac14ffa7c449093068c59562534e1d_85ab63b1 = memo(({children, ...rest}) => {
    const ref_context_name = useRef(null); refs["ref_context_name"] = ref_context_name;
const on_change_015a6c31509a66245c5c157d7feee7a1 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_context_dialog_name", ({ ["name"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ css:({ ["width"] : "100%" }), debounceTimeout:300, element:RadixThemesTextField.Root, id:"context-name", inputRef:ref_context_name, onChange:on_change_015a6c31509a66245c5c157d7feee7a1, placeholder:"Context name", value:(isNotNullOrUndefined(reflex___state____state__cobair___web___state____editor_state.context_dialog_name_rx_state_) ? reflex___state____state__cobair___web___state____editor_state.context_dialog_name_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_8cac14ffa7c449093068c59562534e1d_85ab63b1.displayName = "DebounceInput";
return Debounceinput_debounceinput_8cac14ffa7c449093068c59562534e1d_85ab63b1;
})();

export const Foreach_comp_95c58eb8c3b34ebd9db295ef38b8c3a7_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_95c58eb8c3b34ebd9db295ef38b8c3a7_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.context_dialog_rows_rx_state_ ?? [],((row_rx_state_,index_rx_state_)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"row",key:index_rx_state_,gap:"3"},jsx(DebounceInput,{className:" instantiation-name",css:({ ["width"] : "55%" }),debounceTimeout:300,element:RadixThemesTextField.Root,onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_context_row_name", ({ ["index"] : index_rx_state_, ["name"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),placeholder:"Instantiation",value:(isNotNullOrUndefined(row_rx_state_?.["name"]) ? row_rx_state_?.["name"] : "")},),jsx(DebounceInput,{className:" instantiation-apriori",css:({ ["width"] : "30%" }),debounceTimeout:300,element:RadixThemesTextField.Root,onChange:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_context_row_apriori", ({ ["index"] : index_rx_state_, ["apriori"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))),value:(isNotNullOrUndefined(row_rx_state_?.["apriori"]) ? row_rx_state_?.["apriori"] : "")},),jsx(RadixThemesIconButton,{"aria-label":"Remove instantiation",color:"red",css:({ ["padding"] : "6px" }),onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.remove_context_row", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  })))),size:"1",variant:"ghost"},jsx(LucideX,{size:12},))))))
    )
});
Foreach_comp_95c58eb8c3b34ebd9db295ef38b8c3a7_85ab63b1.displayName = "Foreach";
return Foreach_comp_95c58eb8c3b34ebd9db295ef38b8c3a7_85ab63b1;
})();

export const Button_button_05ddba247897c8d2a41488dcf4044db7_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_05ddba247897c8d2a41488dcf4044db7_85ab63b1 = memo(({children, ...rest}) => {
    const ref_add_instantiation = useRef(null); refs["ref_add_instantiation"] = ref_add_instantiation;
const on_click_eb5ebcfffa0da4ac2a9ace64da37b046 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.add_context_row", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"add-instantiation", onClick:on_click_eb5ebcfffa0da4ac2a9ace64da37b046, ref:ref_add_instantiation, size:"1", variant:"soft" }))},children)
    )
});
Button_button_05ddba247897c8d2a41488dcf4044db7_85ab63b1.displayName = "Button";
return Button_button_05ddba247897c8d2a41488dcf4044db7_85ab63b1;
})();

export const Bare_comp_a08a2063322cf3e3d89c7b7c6220f437_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_a08a2063322cf3e3d89c7b7c6220f437_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.context_dialog_error_rx_state_
    )
});
Bare_comp_a08a2063322cf3e3d89c7b7c6220f437_85ab63b1.displayName = "Bare";
return Bare_comp_a08a2063322cf3e3d89c7b7c6220f437_85ab63b1;
})();

export const Cond_comp_8040195aeb7bcbcf003c37276a06658a_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_8040195aeb7bcbcf003c37276a06658a_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.context_dialog_error_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_8040195aeb7bcbcf003c37276a06658a_85ab63b1.displayName = "Cond";
return Cond_comp_8040195aeb7bcbcf003c37276a06658a_85ab63b1;
})();

export const Button_button_e20d022a5033b549968f843f4b709e5b_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_e20d022a5033b549968f843f4b709e5b_85ab63b1 = memo(({children, ...rest}) => {
    const on_click_b444e16d2fa6eec77b6f2661ea1e71d8 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_context_dialog_open", ({ ["is_open"] : false }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ color:"gray", onClick:on_click_b444e16d2fa6eec77b6f2661ea1e71d8, variant:"soft" }))},children)
    )
});
Button_button_e20d022a5033b549968f843f4b709e5b_85ab63b1.displayName = "Button";
return Button_button_e20d022a5033b549968f843f4b709e5b_85ab63b1;
})();

export const Button_button_1de39b1d5c574102735d52f777ad6ef7_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_1de39b1d5c574102735d52f777ad6ef7_85ab63b1 = memo(({children, ...rest}) => {
    const ref_save_context = useRef(null); refs["ref_save_context"] = ref_save_context;
const on_click_8034cd3811bedb15fb417063f14c7303 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.save_context_dialog", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"save-context", onClick:on_click_8034cd3811bedb15fb417063f14c7303, ref:ref_save_context }))},children)
    )
});
Button_button_1de39b1d5c574102735d52f777ad6ef7_85ab63b1.displayName = "Button";
return Button_button_1de39b1d5c574102735d52f777ad6ef7_85ab63b1;
})();

export const Dialogroot_dialog__root_5ad16e710c671bec838a2d09a613a789_85ab63b1 = /*#__PURE__*/ (() => {
const Dialogroot_dialog__root_5ad16e710c671bec838a2d09a613a789_85ab63b1 = memo(({children, ...rest}) => {
    const on_open_change_603f6d8b1ba86d3b7b59d7ef77887994 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_context_dialog_open", ({ ["is_open"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesDialog.Root,{...mergeSlotProps(rest, ({ onOpenChange:on_open_change_603f6d8b1ba86d3b7b59d7ef77887994, open:reflex___state____state__cobair___web___state____editor_state.context_dialog_open_rx_state_ }))},children)
    )
});
Dialogroot_dialog__root_5ad16e710c671bec838a2d09a613a789_85ab63b1.displayName = "DialogRoot";
return Dialogroot_dialog__root_5ad16e710c671bec838a2d09a613a789_85ab63b1;
})();

export const Bare_comp_8a6ad15235bd5b270f7dc9be22ed3b91_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_8a6ad15235bd5b270f7dc9be22ed3b91_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        ((reflex___state____state__cobair___web___state____editor_state.intention_dialog_index_rx_state_ >= 0) ? "Rename intention" : "New intention")
    )
});
Bare_comp_8a6ad15235bd5b270f7dc9be22ed3b91_85ab63b1.displayName = "Bare";
return Bare_comp_8a6ad15235bd5b270f7dc9be22ed3b91_85ab63b1;
})();

export const Debounceinput_debounceinput_88ede8ae48a3b72c1b06c832fe8315cb_85ab63b1 = /*#__PURE__*/ (() => {
const Debounceinput_debounceinput_88ede8ae48a3b72c1b06c832fe8315cb_85ab63b1 = memo(({children, ...rest}) => {
    const ref_intention_name = useRef(null); refs["ref_intention_name"] = ref_intention_name;
const on_change_f4e13bed6f44f73dd6434a9cb7c36c8e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_intention_dialog_name", ({ ["name"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(DebounceInput,{...mergeSlotProps(rest, ({ css:({ ["width"] : "100%" }), debounceTimeout:300, element:RadixThemesTextField.Root, id:"intention-name", inputRef:ref_intention_name, onChange:on_change_f4e13bed6f44f73dd6434a9cb7c36c8e, placeholder:"Intention name", value:(isNotNullOrUndefined(reflex___state____state__cobair___web___state____editor_state.intention_dialog_name_rx_state_) ? reflex___state____state__cobair___web___state____editor_state.intention_dialog_name_rx_state_ : "") }), "inputRef")},)
    )
});
Debounceinput_debounceinput_88ede8ae48a3b72c1b06c832fe8315cb_85ab63b1.displayName = "DebounceInput";
return Debounceinput_debounceinput_88ede8ae48a3b72c1b06c832fe8315cb_85ab63b1;
})();

export const Bare_comp_cfd677a31ad9bc664e5879e1531b80d6_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_cfd677a31ad9bc664e5879e1531b80d6_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.intention_dialog_error_rx_state_
    )
});
Bare_comp_cfd677a31ad9bc664e5879e1531b80d6_85ab63b1.displayName = "Bare";
return Bare_comp_cfd677a31ad9bc664e5879e1531b80d6_85ab63b1;
})();

export const Cond_comp_4b4c473d0cb9d0a8a247d9fcb0e7e6a0_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_4b4c473d0cb9d0a8a247d9fcb0e7e6a0_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.intention_dialog_error_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_4b4c473d0cb9d0a8a247d9fcb0e7e6a0_85ab63b1.displayName = "Cond";
return Cond_comp_4b4c473d0cb9d0a8a247d9fcb0e7e6a0_85ab63b1;
})();

export const Button_button_f02c8871735b3290b769abfe8707cf42_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_f02c8871735b3290b769abfe8707cf42_85ab63b1 = memo(({children, ...rest}) => {
    const on_click_4035204e58e05dab31ae24aaff3b2bf2 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_intention_dialog_open", ({ ["is_open"] : false }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ color:"gray", onClick:on_click_4035204e58e05dab31ae24aaff3b2bf2, variant:"soft" }))},children)
    )
});
Button_button_f02c8871735b3290b769abfe8707cf42_85ab63b1.displayName = "Button";
return Button_button_f02c8871735b3290b769abfe8707cf42_85ab63b1;
})();

export const Button_button_7b031f6f40540094c7c33dcb7846a3d2_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_7b031f6f40540094c7c33dcb7846a3d2_85ab63b1 = memo(({children, ...rest}) => {
    const ref_save_intention = useRef(null); refs["ref_save_intention"] = ref_save_intention;
const on_click_ee25e4640dc6963cb9e65c4b70cf7c57 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.save_intention_dialog", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"save-intention", onClick:on_click_ee25e4640dc6963cb9e65c4b70cf7c57, ref:ref_save_intention }))},children)
    )
});
Button_button_7b031f6f40540094c7c33dcb7846a3d2_85ab63b1.displayName = "Button";
return Button_button_7b031f6f40540094c7c33dcb7846a3d2_85ab63b1;
})();

export const Dialogroot_dialog__root_4653f68a0c4e76d0964b92d4cce90735_85ab63b1 = /*#__PURE__*/ (() => {
const Dialogroot_dialog__root_4653f68a0c4e76d0964b92d4cce90735_85ab63b1 = memo(({children, ...rest}) => {
    const on_open_change_7f0a937fc222ccfc4765e2756f38ff2a = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_intention_dialog_open", ({ ["is_open"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesDialog.Root,{...mergeSlotProps(rest, ({ onOpenChange:on_open_change_7f0a937fc222ccfc4765e2756f38ff2a, open:reflex___state____state__cobair___web___state____editor_state.intention_dialog_open_rx_state_ }))},children)
    )
});
Dialogroot_dialog__root_4653f68a0c4e76d0964b92d4cce90735_85ab63b1.displayName = "DialogRoot";
return Dialogroot_dialog__root_4653f68a0c4e76d0964b92d4cce90735_85ab63b1;
})();

export const Foreach_comp_f595e5978c9a11d1276063c9d0fcb207_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_f595e5978c9a11d1276063c9d0fcb207_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.intentions_rx_state_ ?? [],((intention_rx_state_,index_rx_state_)=>(jsx(RadixThemesSelect.Item,{key:index_rx_state_,value:(JSON.stringify(index_rx_state_))},intention_rx_state_))))
    )
});
Foreach_comp_f595e5978c9a11d1276063c9d0fcb207_85ab63b1.displayName = "Foreach";
return Foreach_comp_f595e5978c9a11d1276063c9d0fcb207_85ab63b1;
})();

export const Selectroot_select__root_69919f29253e23233bf8d4acdfacc3a0_85ab63b1 = /*#__PURE__*/ (() => {
const Selectroot_select__root_69919f29253e23233bf8d4acdfacc3a0_85ab63b1 = memo(({children, ...rest}) => {
    const on_change_0af8c48a0c832c8b69640ef5034327c2 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_combined_intention", ({ ["index"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_0af8c48a0c832c8b69640ef5034327c2, value:reflex___state____state__cobair___web___state____editor_state.combined_intention_rx_state_ }))},children)
    )
});
Selectroot_select__root_69919f29253e23233bf8d4acdfacc3a0_85ab63b1.displayName = "SelectRoot";
return Selectroot_select__root_69919f29253e23233bf8d4acdfacc3a0_85ab63b1;
})();

export const Foreach_comp_fbe09cb95bebc1a9ea18e9d5136e9e57_85ab63b1 = /*#__PURE__*/ (() => {
const Foreach_comp_fbe09cb95bebc1a9ea18e9d5136e9e57_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.combined_parts_rx_state_ ?? [],((part_rx_state_,index_rx_state_)=>(jsx(RadixThemesFlex,{align:"center",className:"rx-Stack combined-part",css:({ ["width"] : "100%" }),direction:"row",key:index_rx_state_,gap:"3"},jsx(RadixThemesSelect.Root,{onValueChange:((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_combined_part_context", ({ ["index"] : index_rx_state_, ["context_index"] : _ev_0 }), ({  })))], [_ev_0], ({  })))),value:part_rx_state_?.["context"]},jsx(RadixThemesSelect.Trigger,{className:"combined-part-select",css:({ ["flex"] : "1", ["minWidth"] : "0" })},),jsx(RadixThemesSelect.Content,{},Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.contexts_rx_state_ ?? [],((context_rx_state_,context_index_rx_state_)=>(jsx(RadixThemesSelect.Item,{key:context_index_rx_state_,value:(JSON.stringify(context_index_rx_state_))},context_rx_state_?.["name"])))))),jsx(RadixThemesText,{as:"p"},"="),jsx(RadixThemesSelect.Root,{onValueChange:((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_combined_part_instantiation", ({ ["index"] : index_rx_state_, ["instantiation_index"] : _ev_0 }), ({  })))], [_ev_0], ({  })))),value:part_rx_state_?.["instantiation"]},jsx(RadixThemesSelect.Trigger,{className:"combined-part-select",css:({ ["flex"] : "1", ["minWidth"] : "0" })},),jsx(RadixThemesSelect.Content,{},Array.prototype.map.call(reflex___state____state__cobair___web___state____editor_state.contexts_rx_state_?.at?.(part_rx_state_?.["context"])?.["instantiations"] ?? [],((instantiation_rx_state_,instantiation_index_rx_state_)=>(jsx(RadixThemesSelect.Item,{key:instantiation_index_rx_state_,value:(JSON.stringify(instantiation_index_rx_state_))},instantiation_rx_state_?.["name"])))))),jsx(RadixThemesIconButton,{"aria-label":"Remove context",color:"red",css:({ ["padding"] : "6px" }),onClick:((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.remove_combined_part", ({ ["index"] : index_rx_state_ }), ({  })))], [_e], ({  })))),size:"1",variant:"ghost"},jsx(LucideX,{size:12},))))))
    )
});
Foreach_comp_fbe09cb95bebc1a9ea18e9d5136e9e57_85ab63b1.displayName = "Foreach";
return Foreach_comp_fbe09cb95bebc1a9ea18e9d5136e9e57_85ab63b1;
})();

export const Button_button_d5f55c176543b85d1e94e736154ef217_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_d5f55c176543b85d1e94e736154ef217_85ab63b1 = memo(({children, ...rest}) => {
    const ref_add_combined_part = useRef(null); refs["ref_add_combined_part"] = ref_add_combined_part;
const on_click_ff87cccabd70bb9a13c814a2b15d61be = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.add_combined_part", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"add-combined-part", onClick:on_click_ff87cccabd70bb9a13c814a2b15d61be, ref:ref_add_combined_part, size:"1", variant:"soft" }))},children)
    )
});
Button_button_d5f55c176543b85d1e94e736154ef217_85ab63b1.displayName = "Button";
return Button_button_d5f55c176543b85d1e94e736154ef217_85ab63b1;
})();

export const Selectroot_select__root_23a94dd072ae103ebd244ea54543ffff_85ab63b1 = /*#__PURE__*/ (() => {
const Selectroot_select__root_23a94dd072ae103ebd244ea54543ffff_85ab63b1 = memo(({children, ...rest}) => {
    const on_change_b58930607019f7e69b808bcdd4ee69b3 = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_combined_value", ({ ["value"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesSelect.Root,{...mergeSlotProps(rest, ({ onValueChange:on_change_b58930607019f7e69b808bcdd4ee69b3, size:"1", value:reflex___state____state__cobair___web___state____editor_state.combined_value_rx_state_ }))},children)
    )
});
Selectroot_select__root_23a94dd072ae103ebd244ea54543ffff_85ab63b1.displayName = "SelectRoot";
return Selectroot_select__root_23a94dd072ae103ebd244ea54543ffff_85ab63b1;
})();

export const Bare_comp_118b5717795e3f5cc1136e304e2183e0_85ab63b1 = /*#__PURE__*/ (() => {
const Bare_comp_118b5717795e3f5cc1136e304e2183e0_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        reflex___state____state__cobair___web___state____editor_state.combined_error_rx_state_
    )
});
Bare_comp_118b5717795e3f5cc1136e304e2183e0_85ab63b1.displayName = "Bare";
return Bare_comp_118b5717795e3f5cc1136e304e2183e0_85ab63b1;
})();

export const Cond_comp_e91d9ba3c60d7a8cef493616ed04a3c9_85ab63b1 = /*#__PURE__*/ (() => {
const Cond_comp_e91d9ba3c60d7a8cef493616ed04a3c9_85ab63b1 = memo(({children}) => {
    const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        (!((reflex___state____state__cobair___web___state____editor_state.combined_error_rx_state_?.valueOf?.() === ""?.valueOf?.()))?(children?.at?.(0)):(children?.at?.(1)))
    )
});
Cond_comp_e91d9ba3c60d7a8cef493616ed04a3c9_85ab63b1.displayName = "Cond";
return Cond_comp_e91d9ba3c60d7a8cef493616ed04a3c9_85ab63b1;
})();

export const Button_button_1a881908284f96e4a224f5beadb7b238_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_1a881908284f96e4a224f5beadb7b238_85ab63b1 = memo(({children, ...rest}) => {
    const on_click_4d6229f8b282fb8c1139b874c3ebec07 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_combined_dialog_open", ({ ["is_open"] : false }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ color:"gray", onClick:on_click_4d6229f8b282fb8c1139b874c3ebec07, variant:"soft" }))},children)
    )
});
Button_button_1a881908284f96e4a224f5beadb7b238_85ab63b1.displayName = "Button";
return Button_button_1a881908284f96e4a224f5beadb7b238_85ab63b1;
})();

export const Button_button_06c72df5f9373960b38f69c9a461fcb7_85ab63b1 = /*#__PURE__*/ (() => {
const Button_button_06c72df5f9373960b38f69c9a461fcb7_85ab63b1 = memo(({children, ...rest}) => {
    const ref_save_combined = useRef(null); refs["ref_save_combined"] = ref_save_combined;
const on_click_d2f6743152c29b957adc56aa83c0e9c6 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.save_combined_dialog", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])



    return(
        jsx(RadixThemesButton,{...mergeSlotProps(rest, ({ id:"save-combined", onClick:on_click_d2f6743152c29b957adc56aa83c0e9c6, ref:ref_save_combined }))},children)
    )
});
Button_button_06c72df5f9373960b38f69c9a461fcb7_85ab63b1.displayName = "Button";
return Button_button_06c72df5f9373960b38f69c9a461fcb7_85ab63b1;
})();

export const Dialogroot_dialog__root_dbebbd6e8c9a3957cac67344f50cf5b5_85ab63b1 = /*#__PURE__*/ (() => {
const Dialogroot_dialog__root_dbebbd6e8c9a3957cac67344f50cf5b5_85ab63b1 = memo(({children, ...rest}) => {
    const on_open_change_65592eefc9eb37d00acc8dcc192a1bfc = useCallback(((_ev_0) => (addEvents([(ReflexEvent("reflex___state____state.cobair___web___state____editor_state.set_combined_dialog_open", ({ ["is_open"] : _ev_0 }), ({  })))], [_ev_0], ({  })))), [addEvents, ReflexEvent])
const reflex___state____state__cobair___web___state____editor_state = useContext(StateContexts.reflex___state____state__cobair___web___state____editor_state)



    return(
        jsx(RadixThemesDialog.Root,{...mergeSlotProps(rest, ({ onOpenChange:on_open_change_65592eefc9eb37d00acc8dcc192a1bfc, open:reflex___state____state__cobair___web___state____editor_state.combined_dialog_open_rx_state_ }))},children)
    )
});
Dialogroot_dialog__root_dbebbd6e8c9a3957cac67344f50cf5b5_85ab63b1.displayName = "DialogRoot";
return Dialogroot_dialog__root_dbebbd6e8c9a3957cac67344f50cf5b5_85ab63b1;
})();
