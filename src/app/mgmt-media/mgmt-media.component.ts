import { Component, OnInit } from '@angular/core';

import { LocationService } from '../location.service';

@Component({
  selector: 'app-mgmt-media',
  templateUrl: './mgmt-media.component.html',
  styleUrls: ['./mgmt-media.component.css']
})
export class MgmtMediaComponent implements OnInit {
  items: any[] = [];
  cont: number = 0;

  constructor(private locationService: LocationService) { }

  ngOnInit() {
    this.getItems();
  }
  
  getItems() {
    this.locationService.getAllMedia(this.cont)
      .subscribe(resp => this.items = resp.items);
  }

}
