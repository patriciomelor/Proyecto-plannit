/// <reference types="datatables.net" />
/// <reference types="jquery" />

export declare type IFormatter = (this: Editor, val: any, field: Field, def?: any) => any;
/**
 * Initialisation options that can be given to Editor.Field at initialisation
 * time.
 */
export interface IDefaults {
	/**
	 * Class name to assign to the field's container element (in addition to the other
	 * classes that Editor assigns by default).
	 */
	className: string;
	/**
	 * Define a custom comparison function for the field's data.
	 */
	compare: null | ((submitted: any, original: any) => boolean);
	/**
	 * The data property (`mData` in DataTables terminology) that is used to
	 * read from and write to the table. If not given then it will take the same
	 * value as the `name` that is given in the field object. Note that `data`
	 * can be given as null, which will result in Editor not using a DataTables
	 * row property for the value of the field for either getting or setting
	 * data.
	 *
	 * In previous versions of Editor (1.2-) this was called `dataProp`. The old
	 * name can still be used for backwards compatibility, but the new form is
	 * preferred.
	 */
	data: string;
	/**
	 * The default value for the field. Used when creating new rows (editing will
	 * use the currently set value). If given as a function the function will be
	 * executed and the returned value used as the default
	 *
	 * In Editor 1.2 and earlier this field was called `default` - however
	 * `default` is a reserved word in Javascript, so it couldn't be used
	 * unquoted. `default` will still work with Editor 1.3, but the new property
	 * name of `def` is preferred.
	 */
	def: string;
	/**
	 * Control the decoding of HTML entities in input elements.
	 */
	entityDecode: boolean;
	/**
	 * Helpful information text about the field that is shown below the input control.
	 */
	fieldInfo: string;
	/**
	 * Apply a transform (a format) to the value read from a field.
	 */
	getFormatter: IFormatter;
	/**
	 * The ID of the field. This is used by the `label` HTML tag as the "for" attribute
	 * improved accessibility. Although this using this parameter is not mandatory,
	 * it is a good idea to assign the ID to the DOM element that is the input for the
	 * field (if this is applicable).
	 */
	id: string;
	/**
	 * The label to display for the field input (i.e. the name that is visually
	 * assigned to the field).
	 */
	label: string;
	/**
	 * Helpful information text about the field that is shown below the field label.
	 */
	labelInfo: string;
	/**
	 * The name for the field that is submitted to the server. This is the only
	 * mandatory parameter in the field description object.
	 */
	name: string;
	/**
	 * If `null` values should be replaced with the default value on edit
	 */
	nullDefault: boolean;
	/**
	 * The input control that is presented to the end user. The options available
	 * are defined by {@link Editor.fieldTypes} and any extensions made
	 * to that object.
	 */
	type: string;
	/**
	 * Information message for the field - expected to be dynamic
	 */
	message: string;
	/**
	 * Allow a field to be editable when multiple rows are selected
	 */
	multiEditable: boolean;
	/**
	 * Apply a transform (format) to a value when it is set into the field
	 */
	setFormatter: IFormatter;
	/**
	 * Indicate if the field's value can be submitted
	 */
	submit: boolean;
}
export interface IOptions extends Partial<IDefaults> {
}
declare class Field {
	static defaults: IDefaults;
	static formatters: {
		[name: string]: IFormatter;
	};
	private s;
	private dom;
	constructor(options: IOptions, classes: any, host: Editor);
	def(set?: any): any;
	disable(): this;
	displayed(): boolean;
	enable(toggle?: boolean): this;
	enabled(): boolean;
	error(msg: any, fn?: any): any;
	fieldInfo(msg: any): any;
	isMultiValue(): boolean;
	inError(): boolean;
	input(): any;
	focus(): this;
	get(): any;
	hide(animate: any): this;
	label(str: any): string | this;
	labelInfo(msg: any): any;
	message(msg: any, fn?: any): any;
	multiGet(id?: any): any;
	multiRestore(): void;
	multiSet(id: any, val?: any): this;
	name(): string;
	node(): HTMLElement;
	nullDefault(): boolean;
	processing(): boolean;
	processing(set: boolean): this;
	set(val: any, multiCheck?: boolean): this;
	show(animate?: boolean, toggle?: boolean): this;
	update(options: any, append?: boolean): this;
	val(val?: any): any;
	compare(value: any, original: any): boolean;
	dataSrc(): string;
	destroy(): this;
	multiEditable(): boolean;
	multiIds(): string[];
	multiInfoShown(show: any): void;
	multiReset(): void;
	submittable(): boolean;
	valFromData: (a: any) => any;
	valToData: (a: any) => any;
	private _errorNode;
	private _format;
	_msg(el: any, msg?: any, fn?: any): any;
	_multiValueCheck(): boolean;
	_typeFn(name: any, ...args: any[]): any;
}
export interface IFormOptions {
	/** Which element to focus on when the form is shown */
	focus: null | number | string;
	/** Action to take when a background element is activated */
	onBackground: "blur" | "close" | "none" | "submit" | ((editor: Editor) => void);
	/** Action to take when the form is blurred */
	onBlur: "submit" | "close" | "none" | ((editor: Editor) => void);
	/** Action to occur after Ajax update */
	onComplete: "close" | "none" | ((editor: Editor) => void);
	/** What action to perform when pressing escape key */
	onEsc: "blur" | "close" | "none" | "submit" | ((editor: Editor, e: JQuery.TriggeredEvent) => void);
	/** What to do with a JSON returned error for a field */
	onFieldError: "focus" | "none" | ((editor: Editor) => void);
	/** Action to take on return key when the form is focused */
	onReturn: "submit" | "none" | ((editor: Editor, e: JQuery.TriggeredEvent) => void);
	/** What values should be submitted to the server */
	submit: "all" | "changed" | "allIfChanged";
	/** Position to insert a submit button (inline editing) */
	submitTrigger: null | HTMLElement | JQuery | number;
	/** HTML to insert for submit button (inline editing) */
	submitHtml: string;
	/** What data should be loaded into the form */
	scope: "row" | "cell";
	/** Buttons to be displayed in the form footer (e.g. submit button) */
	buttons: any;
	/** DataTables draw type when updating the table */
	drawType: "full-reset" | "full-hold" | "page" | "none" | false | true;
	/** Form message */
	message: string | boolean;
	/** Tell the display controller to nest down */
	nest: boolean;
	/** Form title */
	title: string | boolean;
}
export declare type IMode = null | "bubble" | "inline" | "main";
export declare type IDisplay = false | "bubble" | "inline" | "main";
export interface IAjaxOptions extends JQueryAjaxSettings {
	deleteBody?: boolean;
	data: (d: object) => object | void;
}
/**
 * Settings object for Editor - this provides the state for each instance of
 * Editor and can be accessed through the instance's `s` property. Note that the
 * settings object is considered to be "private" and thus is liable to change
 * between versions. As such if you do read any of the setting parameters,
 * please keep this in mind when upgrading!
 */
export interface ISettings {
	ajax: string | IAjaxOptions | Function;
	opts: any;
	/**
	 * The display controller object for the Form.
	 * This is directly set by the initialisation parameter / default of the same name.
	 */
	displayController: any;
	dataSource: any;
	/**
	 * The form fields - see {@link Editor.models.field} for details of the
	 * objects held in this array.
	 */
	fields: {
		[k: string]: Field;
	};
	/** Global error message */
	globalError: string;
	/**
	 * Field order - order that the fields will appear in on the form. Array of strings,
	 * the names of the fields.
	 */
	order: string[];
	/**
	 * The ID of the row being edited (set to -1 on create and remove actions)
	 */
	id: number;
	/**
	 * Flag to indicate if the form is currently displayed or not and what type of display
	 */
	displayed: IDisplay;
	/**
	 * Flag to indicate if the form is current in a processing state (true) or not (false)
	 */
	processing: boolean;
	/**
	 * Developer provided identifier for the elements to be edited (i.e. at
	 * `dt-type row-selector` to select rows to edit or delete.
	 */
	modifier: any;
	/**
	 * The current form action - 'create', 'edit' or 'remove'. If no current action then
	 * it is set to null.
	 */
	action: null | "create" | "edit" | "remove";
	/**
	 * JSON property from which to read / write the row's ID property.
	 */
	idSrc: string | number;
	/**
	 * Unique instance counter to be able to remove events
	 */
	unique: number;
	/**
	 * Selector for the DataTable
	 */
	table: string | HTMLElement | JQuery;
	/**
	 * Form editing mode
	 */
	mode: IMode;
	editFields: {
		[idSrc: string]: {
			idSrc?: string;
			data?: any;
			node?: HTMLElement;
			fields: {
				[name: string]: Field;
			};
			type?: "row" | "cell";
			attach?: HTMLElement[];
		};
	};
	editOpts: any;
	closeCb: null | ((complete: Function, mode: IMode) => void);
	closeIcb: null | (() => void);
	formOptions: {
		bubble: IFormOptions;
		inline: IFormOptions;
		main: IFormOptions;
	};
	template: JQuery;
	includeFields: string[];
	editData: {
		[field: string]: {
			[id: string]: any;
		};
	};
	setFocus: Field | JQuery;
	editCount: number;
	/** Name of the parameter used to indicate what action Editor is performing */
	actionName: string;
	bubbleNodes: HTMLElement[];
}
declare const settings: ISettings;
declare const _default: {
	/**
	 * Applied to the base DIV element that contains all other Editor elements
	 */
	wrapper: string;
	/**
	 * Processing classes
	 *  @namespace
	 */
	processing: {
		/**
		 * Processing indicator element
		 */
		indicator: string;
		/**
		 * Added to the base element ("wrapper") when the form is "processing"
		 */
		active: string;
	};
	/**
	 * Display header classes
	 *  @namespace
	 */
	header: {
		/**
		 * Container for the header elements
		 */
		wrapper: string;
		/**
		 * Liner for the header content
		 */
		content: string;
	};
	/**
	 * Display body classes
	 *  @namespace
	 */
	body: {
		/**
		 * Container for the body elements
		 */
		wrapper: string;
		/**
		 * Liner for the body content
		 */
		content: string;
	};
	/**
	 * Display footer classes
	 *  @namespace
	 */
	footer: {
		/**
		 * Container for the footer elements
		 */
		wrapper: string;
		/**
		 * Liner for the footer content
		 */
		content: string;
	};
	/**
	 * Form classes
	 *  @namespace
	 */
	form: {
		/**
		 * Container for the form elements
		 */
		wrapper: string;
		/**
		 * Liner for the form content
		 */
		content: string;
		/**
		 * Applied to the <form> tag
		 */
		tag: string;
		/**
		 * Global form information
		 */
		info: string;
		/**
		 * Global error imformation
		 */
		error: string;
		/**
		 * Buttons container
		 */
		buttons: string;
		/**
		 * Button
		 */
		button: string;
		/**
		 * Button inside the form
		 */
		buttonInternal: string;
	};
	/**
	 * Field classes
	 *  @namespace
	 */
	field: {
		/**
		 * Container for each field
		 */
		wrapper: string;
		/**
		 * Class prefix for the field type - field type is added to the end allowing
		 * styling based on field type.
		 */
		typePrefix: string;
		/**
		 * Class prefix for the field name - field name is added to the end allowing
		 * styling based on field name.
		 */
		namePrefix: string;
		/**
		 * Field label
		 */
		label: string;
		/**
		 * Field input container
		 */
		input: string;
		/**
		 * Input elements wrapper
		 */
		inputControl: string;
		/**
		 * Field error state (added to the field.wrapper element when in error state
		 */
		error: string;
		/**
		 * Label information text
		 */
		"msg-label": string;
		/**
		 * Error information text
		 */
		"msg-error": string;
		/**
		 * Live messaging (API) information text
		 */
		"msg-message": string;
		/**
		 * General information text
		 */
		"msg-info": string;
		/**
		 * Multi-value information display wrapper
		 */
		multiValue: string;
		/**
		 * Multi-value information descriptive text
		 */
		multiInfo: string;
		/**
		 * Multi-value information display
		 */
		multiRestore: string;
		/**
		 * Multi-value not editable (field.multiEditable)
		 */
		multiNoEdit: string;
		/**
		 * Field is disabled
		 */
		disabled: string;
		/**
		 * Field's processing element
		 */
		processing: string;
	};
	/**
	 * Action classes - these are added to the Editor base element ("wrapper")
	 * and allows styling based on the type of form view that is being employed.
	 *  @namespace
	 */
	actions: {
		/**
		 * Editor is in 'create' state
		 */
		create: string;
		/**
		 * Editor is in 'edit' state
		 */
		edit: string;
		/**
		 * Editor is in 'remove' state
		 */
		remove: string;
	};
	/**
	 * Inline editing classes - these are used to display the inline editor
	 *  @namespace
	 */
	inline: {
		wrapper: string;
		liner: string;
		buttons: string;
	};
	/**
	 * Bubble editing classes - these are used to display the bubble editor
	 *  @namespace
	 */
	bubble: {
		/**
		 * Bubble container element
		 */
		wrapper: string;
		/**
		 * Bubble content liner
		 */
		liner: string;
		/**
		 * Bubble table display wrapper, so the buttons and form can be shown
		 * as table cells (via css)
		 */
		table: string;
		/**
		 * Close button
		 */
		close: string;
		/**
		 * Pointer shown which node is being edited
		 */
		pointer: string;
		/**
		 * Fixed background
		 */
		bg: string;
	};
};
declare function add(this: Editor, cfg: any, after?: string, reorder?: boolean): Editor;
declare function ajax(this: Editor, newAjax: any): string | Function | Editor | IAjaxOptions;
declare function background(this: Editor): Editor;
declare function blur(this: Editor): Editor;
declare function bubble(this: Editor, cells: any, fieldNames: any, show: any, opts?: any): Editor;
declare function bubblePosition(this: Editor): Editor;
declare function buttons(this: Editor, buttons: any): Editor;
declare function clear(this: Editor, fieldName?: any): Editor;
declare function close(this: Editor): Editor;
declare function create(this: Editor, arg1: any, arg2: any, arg3: any, arg4: any): Editor;
declare function undependent(this: Editor, parent: any): Editor;
declare function dependent(this: Editor, parent: any, url: any, opts: any): Editor;
declare function destroy(this: Editor): void;
declare function disable(this: Editor, name: any): Editor;
declare function display(): IDisplay;
declare function display(show: boolean): Editor;
declare function displayed(this: Editor): (string | number)[];
declare function displayNode(this: Editor): any;
declare function edit(this: Editor, items: any, arg1: any, arg2: any, arg3: any, arg4: any): Editor;
declare function enable(this: Editor, name: any): Editor;
declare function error(this: Editor): Editor;
declare function error(this: Editor, msg: string): Editor;
declare function error(this: Editor, name: string, msg: string): Editor;
declare function field(this: Editor, name: any): Field;
declare function fields(this: Editor): (string | number)[];
declare function file(name: string, id: string | number): any;
declare function files(name: string): any;
declare function get(this: Editor, name: any): any;
declare function hide(this: Editor, names: any, animate: any): Editor;
declare function ids(this: Editor, includeHash?: boolean): (string | number)[];
declare function inError(this: Editor, inNames: any): boolean;
declare function inline(this: Editor, cell: any, fieldName: any, opts: any): Editor;
declare function inlineCreate(this: Editor, insertPoint: null | "start" | "end" | HTMLElement, opts: IFormOptions): Editor;
declare function message(this: Editor, name: any, msg?: any): Editor;
declare function mode(this: Editor, mode: any): Editor | "create" | "edit" | "remove";
declare function modifier(this: Editor): any;
declare function multiGet(this: Editor, fieldNames: any): any;
declare function multiSet(this: Editor, fieldNames: any, val: any): Editor;
declare function node(this: Editor, name: any): HTMLElement | HTMLElement[];
declare function off(this: Editor, name: any, fn: any): Editor;
declare function on(this: Editor, name: any, fn: any): Editor;
declare function one(this: Editor, name: any, fn: any): Editor;
declare function open(this: Editor): Editor;
declare function order(this: Editor): string[];
declare function order(this: Editor, set: string[]): any;
declare function order(this: Editor, ...set: string[]): any;
declare function remove(this: Editor, items: any, arg1: any, arg2: any, arg3: any, arg4: any): Editor;
declare function set(this: Editor, set: any, val: any): Editor;
declare function show(this: Editor, names: any, animate: any): Editor;
declare function submit(this: Editor, successCallback?: any, errorCallback?: any, formatdata?: any, hide?: any): Editor;
declare function table(this: Editor, set: any): string | HTMLElement | Editor | JQuery<HTMLElement>;
declare function template(this: Editor, set: any): Editor | JQuery<HTMLElement>;
declare function title(this: Editor, title: any): string | Editor;
declare function val(this: Editor): any;
declare function val(this: Editor, field: string): any;
declare function val(this: Editor, field: string, value: any): Editor;
declare function error(msg: string, tn: number, thro?: boolean): void;
declare function pairs(data: any, props: any, fn: any): void;
declare function upload(editor: any, conf: any, files: any, progressCallback: any, completeCallback: any): void;
declare function _actionClass(this: Editor): void;
declare function _ajax(this: Editor, data: any, success: any, error: any, submitParams: any): void;
declare function _animate(this: Editor, target: any, style: any, time?: any, callback?: any): void;
declare function _assembleMain(this: Editor): void;
declare function _blur(this: Editor): void;
declare function _clearDynamicInfo(this: Editor, errorsOnly?: boolean): void;
declare function _close(this: Editor, submitComplete?: any, mode?: any): void;
declare function _closeReg(this: Editor, fn: any): void;
declare function _crudArgs(this: Editor, arg1: any, arg2: any, arg3: any, arg4: any): {
	opts: any;
	maybeOpen: () => void;
};
declare function _dataSource(this: Editor, name: any, ...args: any[]): any;
declare function _displayReorder(this: Editor, includeFields?: any): void;
declare function _edit(this: Editor, items: any, editFields: any, type: any, formOptions: any, setupDone: any): void;
declare function _event(this: Editor, trigger: any, args?: any[], promiseComplete?: any): any;
declare function _eventName(this: Editor, input: any): any;
declare function _fieldFromNode(this: Editor, node: any): any;
declare function _fieldNames(this: Editor, fieldNames: any): any[];
declare function _focus(this: Editor, fieldsIn: any, focus: any): void;
declare function _formOptions(this: Editor, opts: IFormOptions): string;
declare function _inline(this: Editor, editFields: any, opts: any, closeCb?: any): Editor;
declare function _optionsUpdate(this: Editor, json: any): void;
declare function _message(this: Editor, el: any, msg: any, title?: any, fn?: any): void;
declare function _multiInfo(this: Editor): void;
declare function _nestedClose(this: Editor, cb: Function): void;
declare function _nestedOpen(this: Editor, cb: Function, nest: boolean): void;
declare function _postopen(this: Editor, type: any, immediate: any): boolean;
declare function _preopen(this: Editor, type: any): boolean;
declare function _processing(this: Editor, processing: any): void;
declare function _noProcessing(this: Editor, args: any): boolean;
declare function _submit(this: Editor, successCallback: any, errorCallback: any, formatdata: any, hide: any): void;
declare function _submitTable(this: Editor, data: any, success: any, error: any, submitParams: any): void;
declare function _submitSuccess(this: Editor, json: any, notGood: any, submitParams: any, submitParamsLocal: any, action: any, editCount: any, hide: any, successCallback: any, errorCallback: any, xhr: any): void;
declare function _submitError(this: Editor, xhr: any, err: any, thrown: any, errorCallback: any, submitParams: any, action: any): void;
declare function _tidy(this: Editor, fn: any): boolean;
declare function _weakInArray(this: Editor, name: any, arr: any): number;
export interface IFieldType {
	create: (conf: any) => JQuery | void;
	get: (conf: any) => any;
	set: (conf: any, val: any) => void;
	enable?: (conf: any) => void;
	disable?: (conf: any) => void;
}
export interface IButton {
	/** Callback for when the button is activated */
	action: () => {};
	/** Class names to give the button */
	className: string;
	/**Set the tab index attribute for the button */
	tabIndex: number;
	/** Text to show in the button */
	text: string;
}
export interface IDisplayController {
	/** Initialisation method, called by Editor when itself, initialises. */
	init: (editor: Editor) => void;
	/** Display the form (add it to the visual display in the document) */
	open: (editor: Editor, append: HTMLElement, fn: Function) => void;
	/** Hide the form (remove it form the visual display in the document) */
	close: (editor: Editor, fn: Function) => void;
	/** Get the container node */
	node: (editor: Editor) => HTMLElement | void;
	[others: string]: any;
}
export default class Editor {
	static fieldTypes: {
		[type: string]: IFieldType;
	};
	static files: {};
	static version: string;
	static classes: {
		wrapper: string;
		processing: {
			indicator: string;
			active: string;
		};
		header: {
			wrapper: string;
			content: string;
		};
		body: {
			wrapper: string;
			content: string;
		};
		footer: {
			wrapper: string;
			content: string;
		};
		form: {
			wrapper: string;
			content: string;
			tag: string;
			info: string;
			error: string;
			buttons: string;
			button: string;
			buttonInternal: string;
		};
		field: {
			wrapper: string;
			typePrefix: string;
			namePrefix: string;
			label: string;
			input: string;
			inputControl: string;
			error: string;
			"msg-label": string;
			"msg-error": string;
			"msg-message": string;
			"msg-info": string;
			multiValue: string;
			multiInfo: string;
			multiRestore: string;
			multiNoEdit: string;
			disabled: string;
			processing: string;
		};
		actions: {
			create: string;
			edit: string;
			remove: string;
		};
		inline: {
			wrapper: string;
			liner: string;
			buttons: string;
		};
		bubble: {
			wrapper: string;
			liner: string;
			table: string;
			close: string;
			pointer: string;
			bg: string;
		};
	};
	static Field: typeof Field;
	static DateTime: any;
	static error: typeof error;
	static pairs: typeof pairs;
	static safeId: (id: string) => string;
	static upload: typeof upload;
	static defaults: {
		table: any;
		fields: any[];
		display: string;
		ajax: any;
		idSrc: string;
		events: {};
		i18n: {
			close: string;
			create: {
				button: string;
				title: string;
				submit: string;
			};
			edit: {
				button: string;
				title: string;
				submit: string;
			};
			remove: {
				button: string;
				title: string;
				submit: string;
				confirm: {
					_: string;
					"1": string;
				};
			};
			error: {
				system: string;
			};
			multi: {
				title: string;
				info: string;
				restore: string;
				noMulti: string;
			};
			datetime: {
				previous: string;
				next: string;
				months: string[];
				weekdays: string[];
				amPm: string[];
				hours: string;
				minutes: string;
				seconds: string;
				unknown: string;
			};
		};
		formOptions: {
			bubble: IFormOptions;
			inline: IFormOptions;
			main: IFormOptions;
		};
		actionName: string;
	};
	static models: {
		button: IButton;
		displayController: IDisplayController;
		fieldType: IFieldType;
		formOptions: IFormOptions;
		settings: ISettings;
	};
	static dataSources: {
		dataTable: {
			id: (data: any) => any;
			fakeRow: (insertPoint: "end" | "start") => {
				0: {
					attachFields: any[];
					attach: any[];
					displayFields: {};
					fields: any;
					type: string;
				};
			};
			fakeRowEnd: () => void;
			individual: (identifier: any, fieldNames: any) => {};
			fields: (identifier: any) => {};
			create: (fields: any, data: any) => void;
			edit: (identifier: any, fields: any, data: any, store: any) => void;
			refresh: () => void;
			remove: (identifier: any, fields: any, store: any) => void;
			prep: (action: any, identifier: any, submit: any, json: any, store: any) => void;
			commit: (action: any, identifier: any, data: any, store: any) => void;
		};
		html: {
			id: (data: any) => any;
			initField: (cfg: any) => void;
			individual: (identifier: any, fieldNames: any) => any;
			fields: (identifier: any) => {};
			create: (fields: any, data: any) => void;
			edit: (identifier: any, fields: any, data: any) => void;
			remove: (identifier: any, fields: any) => void;
		};
	};
	static display: {
		envelope: IDisplayController;
		lightbox: IDisplayController;
	};
	protected classes: typeof classNames;
	protected s: typeof modelSettings;
	protected dom: {
		body: HTMLElement;
		bodyContent: HTMLElement;
		buttons: HTMLElement;
		footer: HTMLElement;
		form: HTMLElement;
		formContent: HTMLElement;
		formError: HTMLElement;
		formInfo: HTMLElement;
		header: HTMLElement;
		processing: HTMLElement;
		wrapper: HTMLElement;
	};
	protected i18n: typeof Editor.defaults.i18n;
	add: typeof publicApi.add;
	ajax: typeof publicApi.ajax;
	background: typeof publicApi.background;
	blur: typeof publicApi.blur;
	bubble: typeof publicApi.bubble;
	bubblePosition: typeof publicApi.bubblePosition;
	buttons: typeof publicApi.buttons;
	clear: typeof publicApi.clear;
	close: typeof publicApi.close;
	create: typeof publicApi.create;
	undependent: typeof publicApi.undependent;
	dependent: typeof publicApi.dependent;
	destroy: typeof publicApi.destroy;
	disable: typeof publicApi.disable;
	display: typeof publicApi.display;
	displayed: typeof publicApi.displayed;
	displayNode: typeof publicApi.displayNode;
	edit: typeof publicApi.edit;
	enable: typeof publicApi.enable;
	error: typeof publicApi.error;
	field: typeof publicApi.field;
	fields: typeof publicApi.fields;
	file: typeof publicApi.file;
	files: typeof publicApi.files;
	get: typeof publicApi.get;
	hide: typeof publicApi.hide;
	ids: typeof publicApi.ids;
	inError: typeof publicApi.inError;
	inline: typeof publicApi.inline;
	inlineCreate: typeof publicApi.inlineCreate;
	message: typeof publicApi.message;
	mode: typeof publicApi.mode;
	modifier: typeof publicApi.modifier;
	multiGet: typeof publicApi.multiGet;
	multiSet: typeof publicApi.multiSet;
	node: typeof publicApi.node;
	off: typeof publicApi.off;
	on: typeof publicApi.on;
	one: typeof publicApi.one;
	open: typeof publicApi.open;
	order: typeof publicApi.order;
	remove: typeof publicApi.remove;
	set: typeof publicApi.set;
	show: typeof publicApi.show;
	submit: typeof publicApi.submit;
	table: typeof publicApi.table;
	template: typeof publicApi.template;
	title: typeof publicApi.title;
	val: typeof publicApi.val;
	protected _actionClass: typeof privateApi._actionClass;
	protected _ajax: typeof privateApi._ajax;
	protected _animate: typeof privateApi._animate;
	protected _assembleMain: typeof privateApi._assembleMain;
	protected _blur: typeof privateApi._blur;
	protected _clearDynamicInfo: typeof privateApi._clearDynamicInfo;
	protected _close: typeof privateApi._close;
	protected _closeReg: typeof privateApi._closeReg;
	protected _crudArgs: typeof privateApi._crudArgs;
	protected _dataSource: typeof privateApi._dataSource;
	protected _displayReorder: typeof privateApi._displayReorder;
	protected _edit: typeof privateApi._edit;
	protected _event: typeof privateApi._event;
	protected _eventName: typeof privateApi._eventName;
	protected _fieldFromNode: typeof privateApi._fieldFromNode;
	protected _fieldNames: typeof privateApi._fieldNames;
	protected _focus: typeof privateApi._focus;
	protected _formOptions: typeof privateApi._formOptions;
	protected _inline: typeof privateApi._inline;
	protected _optionsUpdate: typeof privateApi._optionsUpdate;
	protected _message: typeof privateApi._message;
	protected _multiInfo: typeof privateApi._multiInfo;
	protected _nestedClose: typeof privateApi._nestedClose;
	protected _nestedOpen: typeof privateApi._nestedOpen;
	protected _postopen: typeof privateApi._postopen;
	protected _preopen: typeof privateApi._preopen;
	protected _processing: typeof privateApi._processing;
	protected _noProcessing: typeof privateApi._noProcessing;
	protected _submit: typeof privateApi._submit;
	protected _submitTable: typeof privateApi._submitTable;
	protected _submitSuccess: typeof privateApi._submitSuccess;
	protected _submitError: typeof privateApi._submitError;
	protected _tidy: typeof privateApi._tidy;
	protected _weakInArray: typeof privateApi._weakInArray;
	/** @internal */
	internalEvent(name: any, args: any): void;
	/** @internal */
	internalI18n(): {
		close: string;
		create: {
			button: string;
			title: string;
			submit: string;
		};
		edit: {
			button: string;
			title: string;
			submit: string;
		};
		remove: {
			button: string;
			title: string;
			submit: string;
			confirm: {
				_: string;
				"1": string;
			};
		};
		error: {
			system: string;
		};
		multi: {
			title: string;
			info: string;
			restore: string;
			noMulti: string;
		};
		datetime: {
			previous: string;
			next: string;
			months: string[];
			weekdays: string[];
			amPm: string[];
			hours: string;
			minutes: string;
			seconds: string;
			unknown: string;
		};
	};
	/** @internal */
	internalMultiInfo(): void;
	/** @internal */
	internalSettings(): ISettings;
	constructor(init: any);
}

export {};
