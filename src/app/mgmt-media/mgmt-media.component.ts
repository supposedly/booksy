import { Component, OnInit } from '@angular/core';

import { LocationService } from '../location.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-mgmt-media',
  templateUrl: './mgmt-media.component.html',
  styleUrls: ['./mgmt-media.component.css']
})
export class MgmtMediaComponent implements OnInit {
  msg: string = '';
  items: any[] = [];
  cont: number = 0;

  constructor(
    public globals: Globals,
    private locationService: LocationService
  ) {}

  ngOnInit() {
    this.getItems();
  }
  
  getItems() {
    this.locationService.getAllMedia(this.cont)
      .subscribe(resp => this.items = resp.items);
  }
  
  del(mID) {
    this.locationService.deleteItem(mID)
      .subscribe(resp => this.msg = 'Deleted successfully.', err => this.msg = err.error?err.error:'Error.');
  }

}
