import React from 'react';
import ReactDOM from 'react-dom';
import { Viewer } from 'mapillary-js';  // Убедись, что библиотека подключена правильно

function renderMapillary() {
    class ViewerComponent extends React.Component {
        constructor(props) {
            super(props);
            this.containerRef = React.createRef();
        }

        componentDidMount() {
            this.viewer = new Viewer({
                accessToken: 'your-access-token-here',
                container: this.containerRef.current,
                imageId: '498763468214164',
            });
        }

        componentWillUnmount() {
            if (this.viewer) {
                this.viewer.remove();
            }
        }

        render() {
            return <div ref={this.containerRef} style={{ width: '100%', height: '300px' }} />;
        }
    }

    ReactDOM.render(
        <ViewerComponent />,
        document.getElementById('mapillary-viewer')
    );
}

renderMapillary();
