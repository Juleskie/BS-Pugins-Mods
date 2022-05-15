# 

# ba_meta require api 6
# (see https://ballistica.net/wiki/meta-tag-system)


from __future__ import annotations

from typing import TYPE_CHECKING, cast

import ba, random, copy, _ba
from bastd.actor.playerspaz import PlayerSpaz
from ba._settings import Setting
from dataclasses import dataclass
from bastd.actor.scoreboard import Scoreboard
from bastd.ui.playlist import editgame

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional, Callable


@dataclass
class ConfigurableSetting:
    """Defines a user-controllable setting for a game or other entity.

    Category: Gameplay Classes
    """

    name: Any
    default: Any


class New_Window(ba.Window):

    def __init__(self,
                 gametype: Type[ba.GameActivity],
                 sessiontype: Type[ba.Session],
                 config: Optional[Dict[str, Any]],
                 completion_call: Callable[[Optional[Dict[str, Any]]], Any],
                 default_selection: str = None,
                 transition: str = 'in_right',
                 edit_info: Dict[str, Any] = None):
        from ba.internal import (get_unowned_maps, get_filtered_map_name,
                                 get_map_class, get_map_display_string)
        self._configure_window: Optional[ba.Widget] = None
        self._gametype = gametype
        self._sessiontype = sessiontype
        if edit_info is not None:
            self._edit_info = edit_info
        else:
            if config is None:
                self._edit_info = {'editType': 'add'}
            else:
                self._edit_info = {'editType': 'edit'}

        self._r = 'gameSettingsWindow'

        valid_maps = gametype.get_supported_maps(sessiontype)
        if not valid_maps:
            ba.screenmessage(ba.Lstr(resource='noValidMapsErrorText'))
            raise Exception('No valid maps')

        self._settings_defs = gametype.get_available_settings(sessiontype)
        self._completion_call = completion_call
        unowned_maps = get_unowned_maps()
        valid_maps_owned = [m for m in valid_maps if m not in unowned_maps]
        if valid_maps_owned:
            self._map = valid_maps[random.randrange(len(valid_maps_owned))]
        else:
            self._map = valid_maps[random.randrange(len(valid_maps))]

        is_add = (self._edit_info['editType'] == 'add')
        try:
            if (config is not None and 'settings' in config
                    and 'map' in config['settings']):
                filtered_map_name = get_filtered_map_name(
                    config['settings']['map'])
                if filtered_map_name in valid_maps:
                    self._map = filtered_map_name
        except Exception:
            ba.print_exception('Error getting map for editor.')

        if config is not None and 'settings' in config:
            self._settings = config['settings']
        else:
            self._settings = {}

        self._choice_selections: Dict[str, int] = {}

        uiscale = ba.app.ui.uiscale
        width = 720 if uiscale is ba.UIScale.SMALL else 620
        x_inset = 50 if uiscale is ba.UIScale.SMALL else 0
        height = (365 if uiscale is ba.UIScale.SMALL else
                  460 if uiscale is ba.UIScale.MEDIUM else 550)
        spacing = 52
        y_extra = 15
        y_extra2 = 21

        map_tex_name = (get_map_class(self._map).get_preview_texture_name())
        if map_tex_name is None:
            raise Exception('no map preview tex found for' + self._map)
        map_tex = ba.gettexture(map_tex_name)

        top_extra = 20 if uiscale is ba.UIScale.SMALL else 0
        super().__init__(root_widget=ba.containerwidget(
            size=(width, height + top_extra),
            transition=transition,
            scale=(2.19 if uiscale is ba.UIScale.SMALL else
                   1.35 if uiscale is ba.UIScale.MEDIUM else 1.0),
            stack_offset=(0, -17) if uiscale is ba.UIScale.SMALL else (0, 0)))

        btn = ba.buttonwidget(
            parent=self._root_widget,
            position=(45 + x_inset, height - 82 + y_extra2),
            size=(180, 70) if is_add else (180, 65),
            label=ba.Lstr(resource='backText') if is_add else ba.Lstr(
                resource='cancelText'),
            button_type='back' if is_add else None,
            autoselect=True,
            scale=0.75,
            text_scale=1.3,
            on_activate_call=ba.Call(self._cancel))
        ba.containerwidget(edit=self._root_widget, cancel_button=btn)

        add_button = ba.buttonwidget(
            parent=self._root_widget,
            position=(width - (193 + x_inset), height - 82 + y_extra2),
            size=(200, 65),
            scale=0.75,
            text_scale=1.3,
            label=ba.Lstr(resource=self._r +
                          '.addGameText') if is_add else ba.Lstr(
                              resource='doneText'))

        if ba.app.ui.use_toolbars:
            pbtn = _ba.get_special_widget('party_button')
            ba.widget(edit=add_button, right_widget=pbtn, up_widget=pbtn)

        ba.textwidget(parent=self._root_widget,
                      position=(-8, height - 70 + y_extra2),
                      size=(width, 25),
                      text=gametype.get_display_string(),
                      color=ba.app.ui.title_color,
                      maxwidth=235,
                      scale=1.1,
                      h_align='center',
                      v_align='center')

        map_height = 100

        scroll_height = map_height + 10
        scroll_height += spacing * len(self._settings_defs)

        scroll_width = width - (86 + 2 * x_inset)
        self._scrollwidget = ba.scrollwidget(parent=self._root_widget,
                                             position=(44 + x_inset,
                                                       35 + y_extra),
                                             size=(scroll_width, height - 116),
                                             highlight=False,
                                             claims_left_right=True,
                                             claims_tab=True,
                                             selection_loops_to_parent=True)
        self._subcontainer = ba.containerwidget(parent=self._scrollwidget,
                                                size=(scroll_width,
                                                      scroll_height),
                                                background=False,
                                                claims_left_right=True,
                                                claims_tab=True,
                                                selection_loops_to_parent=True)

        v = scroll_height - 5
        h = -40
        widget_column: List[List[ba.Widget]] = []
        ba.textwidget(parent=self._subcontainer,
                      position=(h + 49, v - 63),
                      size=(100, 30),
                      maxwidth=110,
                      text=ba.Lstr(resource='mapText'),
                      h_align='left',
                      color=(0.8, 0.8, 0.8, 1.0),
                      v_align='center')

        ba.imagewidget(
            parent=self._subcontainer,
            size=(256 * 0.7, 125 * 0.7),
            position=(h + 261 - 128 + 128.0 * 0.56, v - 90),
            texture=map_tex,
            model_opaque=ba.getmodel('level_select_button_opaque'),
            model_transparent=ba.getmodel('level_select_button_transparent'),
            mask_texture=ba.gettexture('mapPreviewMask'))
        map_button = btn = ba.buttonwidget(
            parent=self._subcontainer,
            size=(140, 60),
            position=(h + 448, v - 72),
            on_activate_call=ba.Call(self._select_map),
            scale=0.7,
            label=ba.Lstr(resource='mapSelectText'))
        widget_column.append([btn])

        ba.textwidget(parent=self._subcontainer,
                      position=(h + 363 - 123, v - 114),
                      size=(100, 30),
                      flatness=1.0,
                      shadow=1.0,
                      scale=0.55,
                      maxwidth=256 * 0.7 * 0.8,
                      text=get_map_display_string(self._map),
                      h_align='center',
                      color=(0.6, 1.0, 0.6, 1.0),
                      v_align='center')
        v -= map_height

        for setting in self._settings_defs:
            value = setting.default
            value_type = type(value)
            try:
                if (config is not None and 'settings' in config
                        and setting.name in config['settings']):
                    value = value_type(config['settings'][setting.name])
            except Exception:
                ba.print_exception()
            self._settings[setting.name] = value
            self._setting_name = self._settings[setting.name]

            name_translated = self._get_localized_setting_name(setting.name)

            mw1 = 280
            mw2 = 70
            if isinstance(setting, ConfigurableSetting):
                v -= spacing
                txt = ba.textwidget(parent=self._subcontainer,
                              position=(h + 50, v),
                              size=(100, 30),
                              maxwidth=mw1,
                              text=name_translated,
                              h_align='left',
                              color=(0.8, 0.8, 0.8, 1.0),
                              v_align='center')
                editables = ba.buttonwidget(parent=self._subcontainer,
                                       position=(h + 509 - 50 - 1, v),
                                       size=(88, 38),
                                       color=(0.6,0.7,1.0),
                                       label='Configure',
                                       autoselect=True,
                                       on_activate_call=ba.Call(self.edit_configure, setting.name, txt,
                                           setting),
                                       repeat=True)
                widget_column.append(editables)
            elif isinstance(setting, ba.ChoiceSetting):
                for choice in setting.choices:
                    if len(choice) != 2:
                        raise ValueError(
                            "Expected 2-member tuples for 'choices'; got: " +
                            repr(choice))
                    if not isinstance(choice[0], str):
                        raise TypeError(
                            'First value for choice tuple must be a str; got: '
                            + repr(choice))
                    if not isinstance(choice[1], value_type):
                        raise TypeError(
                            'Choice type does not match default value; choice:'
                            + repr(choice) + '; setting:' + repr(setting))
                if value_type not in (int, float):
                    raise TypeError(
                        'Choice type setting must have int or float default; '
                        'got: ' + repr(setting))

                # Start at the choice corresponding to the default if possible.
                self._choice_selections[setting.name] = 0
                for index, choice in enumerate(setting.choices):
                    if choice[1] == value:
                        self._choice_selections[setting.name] = index
                        break

                v -= spacing
                ba.textwidget(parent=self._subcontainer,
                              position=(h + 50, v),
                              size=(100, 30),
                              maxwidth=mw1,
                              text=name_translated,
                              h_align='left',
                              color=(0.8, 0.8, 0.8, 1.0),
                              v_align='center')
                txt = ba.textwidget(
                    parent=self._subcontainer,
                    position=(h + 509 - 95, v),
                    size=(0, 28),
                    text=self._get_localized_setting_name(setting.choices[
                        self._choice_selections[setting.name]][0]),
                    editable=False,
                    color=(0.6, 1.0, 0.6, 1.0),
                    maxwidth=mw2,
                    h_align='right',
                    v_align='center',
                    padding=2)
                btn1 = ba.buttonwidget(parent=self._subcontainer,
                                       position=(h + 509 - 50 - 1, v),
                                       size=(28, 28),
                                       label='<',
                                       autoselect=True,
                                       on_activate_call=ba.Call(
                                           self._choice_inc, setting.name, txt,
                                           setting, -1),
                                       repeat=True)
                btn2 = ba.buttonwidget(parent=self._subcontainer,
                                       position=(h + 509 + 5, v),
                                       size=(28, 28),
                                       label='>',
                                       autoselect=True,
                                       on_activate_call=ba.Call(
                                           self._choice_inc, setting.name, txt,
                                           setting, 1),
                                       repeat=True)
                widget_column.append([btn1, btn2])

            elif isinstance(setting, (ba.IntSetting, ba.FloatSetting)):
                v -= spacing
                min_value = setting.min_value
                max_value = setting.max_value
                increment = setting.increment
                ba.textwidget(parent=self._subcontainer,
                              position=(h + 50, v),
                              size=(100, 30),
                              text=name_translated,
                              h_align='left',
                              color=(0.8, 0.8, 0.8, 1.0),
                              v_align='center',
                              maxwidth=mw1)
                txt = ba.textwidget(parent=self._subcontainer,
                                    position=(h + 509 - 95, v),
                                    size=(0, 28),
                                    text=str(value),
                                    editable=False,
                                    color=(0.6, 1.0, 0.6, 1.0),
                                    maxwidth=mw2,
                                    h_align='right',
                                    v_align='center',
                                    padding=2)
                btn1 = ba.buttonwidget(parent=self._subcontainer,
                                       position=(h + 509 - 50 - 1, v),
                                       size=(28, 28),
                                       label='-',
                                       autoselect=True,
                                       on_activate_call=ba.Call(
                                           self._inc, txt, min_value,
                                           max_value, -increment, value_type,
                                           setting.name),
                                       repeat=True)
                btn2 = ba.buttonwidget(parent=self._subcontainer,
                                       position=(h + 509 + 5, v),
                                       size=(28, 28),
                                       label='+',
                                       autoselect=True,
                                       on_activate_call=ba.Call(
                                           self._inc, txt, min_value,
                                           max_value, increment, value_type,
                                           setting.name),
                                       repeat=True)
                widget_column.append([btn1, btn2])

            elif value_type == bool:
                v -= spacing
                ba.textwidget(parent=self._subcontainer,
                              position=(h + 50, v),
                              size=(100, 30),
                              text=name_translated,
                              h_align='left',
                              color=(0.8, 0.8, 0.8, 1.0),
                              v_align='center',
                              maxwidth=mw1)
                txt = ba.textwidget(
                    parent=self._subcontainer,
                    position=(h + 509 - 95, v),
                    size=(0, 28),
                    text=ba.Lstr(resource='onText') if value else ba.Lstr(
                        resource='offText'),
                    editable=False,
                    color=(0.6, 1.0, 0.6, 1.0),
                    maxwidth=mw2,
                    h_align='right',
                    v_align='center',
                    padding=2)
                cbw = ba.checkboxwidget(parent=self._subcontainer,
                                        text='',
                                        position=(h + 505 - 50 - 5, v - 2),
                                        size=(200, 30),
                                        autoselect=True,
                                        textcolor=(0.8, 0.8, 0.8),
                                        value=value,
                                        on_value_change_call=ba.Call(
                                            self._check_value_change,
                                            setting.name, txt))
                widget_column.append([cbw])

            else:
                raise Exception()

        ba.buttonwidget(edit=add_button, on_activate_call=ba.Call(self._add))
        ba.containerwidget(edit=self._root_widget,
                           selected_child=add_button,
                           start_button=add_button)

        if default_selection == 'map':
            ba.containerwidget(edit=self._root_widget,
                               selected_child=self._scrollwidget)
            ba.containerwidget(edit=self._subcontainer,
                               selected_child=map_button)

    def edit_configure(self, setting_name: str, widget: ba.Widget,
                    setting: ConfigurableSetting):
        c_width = 600
        c_height = 250
        uiscale = ba.app.ui.uiscale
        self._configure_window = cnt = ba.containerwidget(
            scale=(1.8 if uiscale is ba.UIScale.SMALL else
                   1.55 if uiscale is ba.UIScale.MEDIUM else 1.0),
            size=(c_width, c_height),
            transition='in_scale')
        ba.textwidget(parent=cnt,
                      size=(0, 0),
                      h_align='center',
                      v_align='center',
                      text="Field Editor",
                      maxwidth=c_width * 0.8,
                      position=(c_width * 0.5, c_height - 60))
        self._field_name = txt = ba.textwidget(
            parent=cnt,
            size=(c_width * 0.8, 40),
            h_align='left',
            v_align='center',
            text=str(self._settings[setting_name]),
            editable=True,
            position=(c_width * 0.1, c_height - 140),
            autoselect=True,
            maxwidth=c_width * 0.7,
            max_chars=200)
        cbtn = ba.buttonwidget(
            parent=cnt,
            label="Exit",
            on_activate_call=ba.Call(
                lambda c: ba.containerwidget(edit=c, transition='out_scale'),
                cnt),
            size=(180, 60),
            position=(30, 30),
            autoselect=True)
        if setting_name == 'Disabled Powerups':
           _ba.set_party_window_open(False)
           _ba.set_party_icon_always_visible(True)
           _ba.chatmessage("=====Raw codes of the powerups====")
           _ba.chatmessage("Triple Bomb = triple_bombs")
           _ba.chatmessage("Impact Bomb = impact_bombs")
           _ba.chatmessage("Frozen Bomb = ice_bombs")
           _ba.chatmessage("Sticky Bomb = sticky_bombs")
           _ba.chatmessage("Landmine = land_mines")
           _ba.chatmessage("Med Kit = health")
           _ba.chatmessage("Curse = curse")
           _ba.chatmessage("Punch = punch")
           _ba.chatmessage("Shield = shield")
           _ba.chatmessage("To add a powerup simply type its raw code in the field and add quote on both sides.")
           _ba.chatmessage("Like this: \'sticky_bombs\'")
           _ba.chatmessage("To add multiple powerups, seperate them with commas like this")
           _ba.chatmessage("\'punch\', \'shield\', \'health\', \'curse\'")
           _ba.chatmessage("------------------------------------------------------")
           _ba.chatmessage("------------------------------------------------------")
           _ba.chatmessage("Open Party Window for info.")
           _ba.chatmessage("------------------------------------------------------")
           ba.playsound(ba.getsound('mel0' + str(random.randint(0,9))))
        def save():
          ttx: str = cast(str, ba.textwidget(query=self._field_name))
          self._settings[setting_name] = ttx
          ba.containerwidget(edit=cnt, transition='out_scale')
        okb = ba.buttonwidget(parent=cnt,
                              label="Save",
                              size=(180, 60),
                              position=(c_width - 230, 30),
                              on_activate_call=ba.Call(save),
                              autoselect=True)
        ba.widget(edit=cbtn, right_widget=okb)
        ba.widget(edit=okb, left_widget=cbtn)
        ba.textwidget(edit=txt, on_return_press_call=okb.activate)
        ba.containerwidget(edit=cnt, cancel_button=cbtn, start_button=okb)
      
    def _get_localized_setting_name(self, name: str) -> ba.Lstr:
        return ba.Lstr(translate=('settingNames', name))

    def _select_map(self) -> None:
        from bastd.ui.playlist.mapselect import PlaylistMapSelectWindow

        ba.containerwidget(edit=self._root_widget, transition='out_left')
        ba.app.ui.set_main_menu_window(
            PlaylistMapSelectWindow(self._gametype, self._sessiontype,
                                    copy.deepcopy(self._getconfig()),
                                    self._edit_info,
                                    self._completion_call).get_root_widget())

    def _choice_inc(self, setting_name: str, widget: ba.Widget,
                    setting: ba.ChoiceSetting, increment: int) -> None:
        choices = setting.choices
        if increment > 0:
            self._choice_selections[setting_name] = min(
                len(choices) - 1, self._choice_selections[setting_name] + 1)
        else:
            self._choice_selections[setting_name] = max(
                0, self._choice_selections[setting_name] - 1)
        ba.textwidget(edit=widget,
                      text=self._get_localized_setting_name(
                          choices[self._choice_selections[setting_name]][0]))
        self._settings[setting_name] = choices[
            self._choice_selections[setting_name]][1]

    def _cancel(self) -> None:
        self._completion_call(None)

    def _check_value_change(self, setting_name: str, widget: ba.Widget,
                            value: int) -> None:
        ba.textwidget(edit=widget,
                      text=ba.Lstr(resource='onText') if value else ba.Lstr(
                          resource='offText'))
        self._settings[setting_name] = value

    def _getconfig(self) -> Dict[str, Any]:
        settings = copy.deepcopy(self._settings)
        settings['map'] = self._map
        return {'settings': settings}

    def _add(self) -> None:
        self._completion_call(copy.deepcopy(self._getconfig()))

    def _inc(self, ctrl: ba.Widget, min_val: Union[int, float],
             max_val: Union[int, float], increment: Union[int, float],
             setting_type: Type, setting_name: str) -> None:
        if setting_type == float:
            val = float(cast(str, ba.textwidget(query=ctrl)))
        else:
            val = int(cast(str, ba.textwidget(query=ctrl)))
        val += increment
        val = max(min_val, min(val, max_val))
        if setting_type == float:
            ba.textwidget(edit=ctrl, text=str(round(val, 2)))
        elif setting_type == int:
            ba.textwidget(edit=ctrl, text=str(int(val)))
        else:
            raise TypeError('invalid vartype: ' + str(setting_type))
        self._settings[setting_name] = val

      
editgame.PlaylistEditGameWindow = New_Window








class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export game
class CustomDeathMatchGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'Custom Death Match'
    description = 'Create death match game in many variations!'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [ba.IntSetting('Kills to Win', min_value=1, default=5, increment=1)]
        if issubclass(sessiontype, ba.FreeForAllSession): settings.append(ba.BoolSetting('Negative Scores', default=False))
        else: pass
        settings += [
            ba.BoolSetting('Epic Mode', default=False),
            ConfigurableSetting("Game Name", default = "Death Match"),
            ConfigurableSetting("Game Description", default = "Crush 5 of your enemies."),
            ConfigurableSetting("Time Limit", default = 180),
            ba.FloatChoiceSetting('Respawn Time', choices=[('Shorterer', 0.15),('Shorter', 0.25),('Short', 0.5),('Normal', 1.0),('Long', 2.0),('Longer', 4.0),('Longerer', 6.0),],default=1.0,),
            ConfigurableSetting("Punch Power (Spaz)", default = 1.2),
            ConfigurableSetting("Impact Scale (Spaz)", default = 1.00),
            ConfigurableSetting("Cooldown (Punch)", default = 400),
            ConfigurableSetting("Cooldown (Bomb)", default = 0),
            ConfigurableSetting("Cooldown (Grab)", default = 0),
            ConfigurableSetting("Cooldown (Jump)", default = 250),
            ConfigurableSetting("HP (Amount)", default = 1000),
            ConfigurableSetting("HP (Maximum)", default = 1000),
            ConfigurableSetting("Powerup Drop Rate", default = 8.0),
            ConfigurableSetting("Blast Radius (Bomb)", default = 2.0),
            ba.BoolSetting('Allow Punch', default=True),
            ba.BoolSetting('Allow Jump', default=True),
            ba.BoolSetting('Allow Pickup', default=True),
            ba.BoolSetting('Allow Bomb', default=True),
            ba.BoolSetting('Allow Run', default=True),
            ConfigurableSetting("Disabled Powerups", default = ""),
            ba.BoolSetting('Enable TNT', default=True),
            ba.BoolSetting('Shatter on Death', default=False),
            ba.BoolSetting('Extreme Shatter on Death', default=False),
            ba.BoolSetting('Explode on Death', default=False),
            ba.ChoiceSetting('Explosion Type', choices=[('Normal', 1),('Icy', 2)],default=1),
            ba.ChoiceSetting('Default Bomb Type', choices=[('Normal', 1),('Sticky', 2),('Impact', 3),('Landmine', 4),('Ice', 5), ('Random', 6), ('Random (For Each)', 7)],default=1),
            ba.IntSetting('Default Bomb Count',min_value=1, increment=1, default=1, ),
            ba.BoolSetting('Permanent Shield', default=False),
            ba.BoolSetting('Permanent Gloves', default=False),
            ba.BoolSetting('Permanent Hockey Speed', default=False),
            ]

        return settings
    
    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: Optional[int] = None
        self._dingsound = ba.getsound('dingSmall')
        # Initiliaze settings
        self.slow_motion = bool(settings['Epic Mode'])
        self._kills_to_win_per_player = int(settings['Kills to Win'])
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(settings.get('Allow Negative Scores', False))
        
        self._game_name = settings['Game Name']
        self._game_desc = settings['Game Description']
        self.s = settings
        # ------------------------------

        # Base class overrides.
        self.default_music = (ba.MusicType.EPIC if self.slow_motion else
                              ba.MusicType.TO_THE_DEATH)

    def get_instance_display_string(self) -> ba.Lstr:
        return self._game_name
    
    def get_instance_description(self) -> Union[str, Sequence]:
        return self._game_desc
    
    def spawn_player(self, player: PlayerType) -> ba.Actor:
        s = self.s
        assert player
        spaz = self.spawn_player_spaz(player)
        assert spaz.node
        spaz.connect_controls_to_player(enable_punch=s['Allow Punch'], enable_jump=s['Allow Jump'], enable_bomb=s['Allow Bomb'], enable_run=s['Allow Run'], enable_pickup=s['Allow Pickup'])
        spaz._punch_power_scale = float(s['Punch Power (Spaz)'])
        spaz.impact_scale = float(s['Impact Scale (Spaz)'])
        spaz._punch_cooldown = float(s['Cooldown (Punch)'])
        spaz._jump_cooldown = float(s['Cooldown (Jump)'])
        spaz._pickup_cooldown = float(s['Cooldown (Grab)'])
        spaz._bomb_cooldown = float(s['Cooldown (Bomb)'])
        spaz.hitpoints = int(s['HP (Amount)'])
        spaz.hitpoints_max = int(s['HP (Maximum)'])
        spaz.bomb_count = int(s['Default Bomb Count'])
        if s['Default Bomb Type'] == 1:
           spaz.bomb_type = 'normal'
        elif s['Default Bomb Type'] == 2:
           spaz.bomb_type = 'sticky'
        elif s['Default Bomb Type'] == 3:
           spaz.bomb_type = 'impact'
        elif s['Default Bomb Type'] == 4:
           spaz.bomb_type = 'land_mine'
        elif s['Default Bomb Type'] == 5:
           spaz.bomb_type = 'ice'
        elif s['Default Bomb Type'] == 6:
           seed = str(random.choice([ice,normal,sticky,impact,land_mine]))
           spaz.bomb_type = seed
        elif s['Default Bomb Type'] == 7:
           spaz.bomb_type = str(random.choice([ice,normal,sticky,impact,land_mine]))
        spaz.blast_radius = float(s['Blast Radius (Bomb)'])
        if bool(s['Permanent Gloves']) == True: spaz.equip_boxing_gloves()
        if bool(s['Permanent Shield']) == True: spaz.equip_shields()
        spaz.node.hockey = False
    
    def handlemessage(self, msg: Any) -> Any:

        s = self.s
        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)
            drama = player.actor
            
            if bool(s['Shatter on Death']) == True:
               drama.node.shattered = 2 if bool(s['Extreme Shatter on Death']) == True else 1
               
            if bool(s['Explode on Death']) == True:
               from bastd.actor.bomb import Blast
               if s['Explosion Type'] == 1:
                   Blast(blast_radius=drama.blast_radius, blast_type='normal', hit_subtype='normal', hit_type='explosion', position=drama.node.position)
               else:
                   Blast(blast_radius=drama.blast_radius, blast_type='ice', hit_subtype='normal', hit_type='explosion', position=drama.node.position)

            killer = msg.getkillerplayer(Player)
            if killer is None:
                return None

            # Handle team-kills.
            if killer.team is player.team:

                # In free-for-all, killing yourself loses you a point.
                if isinstance(self.session, ba.FreeForAllSession):
                    new_score = player.team.score - 1
                    if not self._allow_negative_scores:
                        new_score = max(0, new_score)
                    player.team.score = new_score

                # In teams-mode it gives a point to the other team.
                else:
                    ba.playsound(self._dingsound)
                    for team in self.teams:
                        if team is not killer.team:
                            team.score += 1

            # Killing someone on another team nets a kill.
            else:
                killer.team.score += 1
                ba.playsound(self._dingsound)

                # In FFA show scores since its hard to find on the scoreboard.
                if isinstance(killer.actor, PlayerSpaz) and killer.actor:
                    killer.actor.set_score_text(str(killer.team.score) + '/' +
                                                str(self._score_to_win),
                                                color=killer.team.color,
                                                flash=True)

            self._update_scoreboard()

            # If someone has won, set a timer to end shortly.
            # (allows the dust to clear and draws to occur if deaths are
            # close enough)
            assert self._score_to_win is not None
            if any(team.score >= self._score_to_win for team in self.teams):
                ba.timer(0.5, self.end_game)

        else:
            return super().handlemessage(msg)
        return None

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def setup_standard_powerup_drops(self) -> None:
        """Create standard powerup drops for the current map."""
        # pylint: disable=cyclic-import
        s = self.s
        self._powerup_drop_timer = _ba.Timer(float(s['Powerup Drop Rate']),
                                             ba.WeakCall(
                                                 self._standard_drop_powerups),
                                             repeat=True)
        self._standard_drop_powerups()
        if bool(self.s['Enable TNT']) == True:
            self._tnt_spawners = {}
            self._setup_standard_tnt_drops()
            
    def _standard_drop_powerup(self, index: int, expire: bool = True) -> None:
        # pylint: disable=cyclic-import
        from bastd.actor.powerupbox import PowerupBox, PowerupBoxFactory
        PowerupBox(
            position=self.map.powerup_spawn_points[index],
            poweruptype=PowerupBoxFactory.get().get_random_powerup_type(excludetypes=self.s['Disabled Powerups']),
            expire=expire).autoretain()
    
    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = (self._kills_to_win_per_player *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score,
                                            self._score_to_win)

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
        
    def _show_info(self) -> None:
        from ba._gameutils import animate
        from bastd.actor.zoomtext import ZoomText
        name = self.get_instance_display_string()
        ZoomText(name,
                 maxwidth=800,
                 lifespan=2.5,
                 jitter=2.0,
                 position=(0, 180),
                 flash=False,
                 color=(0.93 * 1.25, 0.9 * 1.25, 1.0 * 1.25),
                 trailcolor=(0.15, 0.05, 1.0, 0.0)).autoretain()
        _ba.timer(0.2, ba.Call(_ba.playsound, _ba.getsound('gong')))

        # The description can be either a string or a sequence with args
        if self.settings_raw.get('Epic Mode', False):
            translation = ""
        
        # to swap in post-translation.
        desc_in = self.get_instance_description()
        desc_l: Sequence
        if isinstance(desc_in, str):
            desc_l = [desc_in]  # handle simple string case
        else:
            desc_l = desc_in
        if not isinstance(desc_l[0], str):
            raise TypeError('Invalid format for instance description')
        subs = []
        for i in range(len(desc_l) - 1):
            subs.append(('${ARG' + str(i + 1) + '}', str(desc_l[i + 1])))
        translation = ba.Lstr(translate=('gameDescriptions', desc_l[0]),
                           subs=subs)
        vrmode = _ba.app.vr_mode
        dnode = _ba.newnode('text',
                            attrs={
                                'v_attach': 'center',
                                'h_attach': 'center',
                                'h_align': 'center',
                                'color': (1, 1, 1, 1),
                                'shadow': 1.0 if vrmode else 0.5,
                                'flatness': 1.0 if vrmode else 0.5,
                                'vr_depth': -30,
                                'position': (0, 80),
                                'scale': 1.2,
                                'maxwidth': 700,
                                'text': translation
                            })
        cnode = _ba.newnode('combine',
                            owner=dnode,
                            attrs={
                                'input0': 1.0,
                                'input1': 1.0,
                                'input2': 1.0,
                                'size': 4
                            })
        cnode.connectattr('output', dnode, 'color')
        keys = {0.5: 0, 1.0: 1.0, 2.5: 1.0, 4.0: 0.0}
        animate(cnode, 'input3', keys)
        _ba.timer(4.0, dnode.delete)
