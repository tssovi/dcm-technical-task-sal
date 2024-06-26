import React, {Component}  from 'react';

class AddNewRequest extends Component {

  render(){

    return (
        <div className="row">
            <div className="col-md-12">
              <fieldset>
                <legend>Upload test</legend>
                <form>
                  <div className="row">
                    <div className="col-md-3 form-group">
                      <select className="form-control" name="upload_dir" id="upload_dir" placeholder="Upload Dir"
                              value={this.props.uploadDir}  onChange={this.props.uploadDirChanged.bind(this)}>
                        <option value="" defaultValue></option>
                          {this.props.assets.upload_dirs && this.props.assets.upload_dirs.map(item => <option value={item} key={item}>{item}</option>)}
                      </select>
                      <p className="error-message">{this.props.uploadDirError}</p>
                    </div>
                    <div className="col-md-3 form-group">
                       <input accept=".py" type="file" name="test_file" id="test_file" key={this.props.testFile} onChange={this.props.testFileChanged.bind(this)}/>
                       <p className="error-message">{this.props.testFileError}</p>
                    </div>
                    <div className="col-md-2">
                      <input type="button" id="submit_test_upload" className="btn btn-primary" value="Submit" disabled={this.props.uploadDir === '' || this.props.testFile === ''} onClick={this.props.uploadTest}/>
                    </div>
                  </div>
                </form>
              </fieldset>
            </div>
          </div>
    );
  }
}

export default AddNewRequest;
