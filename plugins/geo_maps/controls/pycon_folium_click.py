from branca.element import Element, Figure, JavascriptLink, MacroElement
from jinja2 import Template

from common.logging.logger import logger


class PyConFoliumClick(MacroElement):
    _template = Template(
        """
            {% macro script(this, kwargs) %}

                var _the_parent = {{this._parent.get_name()}};

                class PyConFoliumObjs {
                    constructor() {
                        this.marker = null;
                        this.lat_lng = null;
                    }

                    putMarker(lat, lng){
                        if ( this.marker == null ){
                            this.lat_lng = new L.LatLng(lat, lng);
                            this.marker = L.marker(this.lat_lng).addTo(_the_parent);
                        }
                        else{
                            this.lat_lng = new L.LatLng(lat, lng);
                            this.marker.setLatLng(this.lat_lng);
                        }
                    };

                }

                var pyConFoliumObjs = new PyConFoliumObjs();


                function getLatLng(e){
                    var lat = e.latlng.lat.toFixed(6);
                    var lng = e.latlng.lng.toFixed(6);

                    L.marker([lat,lng]).addTo(_the_parent);
                };

                {{this._parent.get_name()}}.on('click', getLatLng);
            {% endmacro %}
        """
    )

    def __init__(self, format_str=None):
        super().__init__()
        self._name = "PyConFoliumClickTest_0"

    def render(self, **kwargs):
        super().render(**kwargs)

        figure = self.get_root()
        assert isinstance(figure, Figure), "You cannot render this Element if it is not in a Figure."

        pycon_style = """
            <style>
                .pycon_center {
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                                    }
            </style>
        """

        figure.header.add_child(Element(pycon_style), name="pycon_style")
