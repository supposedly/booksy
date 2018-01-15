import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { MediaItem } from '../classes';
import { MediaService } from '../media.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-media-info',
  templateUrl: './media-info.component.html',
  styleUrls: ['./media-info.component.css']
})
export class MediaInfoComponent implements OnInit {
  item: MediaItem;
  mID: string;
  msg: string;
  
  constructor(
    public globals: Globals,
    public location: Location,
    private route: ActivatedRoute,
    private mediaService: MediaService
  ) {}
  
  ngOnInit(): void {
    this.mID = this.route.snapshot.paramMap.get('mID');
    this.getItem();
  }
  
  getItem(): void {
    this.mediaService.getInfo(this.mID)
      .subscribe(
        item => {
          this.item = item.info;
          if (this.item.fines == 'None') { // because Python isn't properly serializing None to null for some reason
            this.item.fines = null;
          }
        });
  }
  
  placeOnHold(): void {
    this.mediaService.placeHold(this.mID)
      .subscribe(resp => {}, err => this.msg = err.error?err.error:'Error.');
  }
  
  markFinesPaid(): void {
    this.mediaService.markFinesPaid(this.mID)
      .subscribe(
        resp => {
          this.msg = "Fines have been reset to 0 and will remain so until tomorrow.";
          this.item.fines = null;
        },
        err => this.msg = err.error?err.error:'Error.'
      );
  }

}
